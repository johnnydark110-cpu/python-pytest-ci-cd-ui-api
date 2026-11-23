"""只读模式对 HTTP 写请求的安全门禁测试。"""

from __future__ import annotations

import httpx
import pytest

from core import APIClient, ReadOnlyViolationError

pytestmark = pytest.mark.regression


def test_read_only_client_allows_get_request() -> None:
    """只读模式应允许 GET 并正常调用 transport。"""
    captured: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        captured.append(request.method)
        return httpx.Response(
            status_code=200,
            json={"ok": True},
            request=request,
        )

    with APIClient(
        base_url="https://safe.local",
        read_only=True,
        transport=httpx.MockTransport(handler),
    ) as client:
        response = client.get("/api/orders")

        assert client.read_only is True

    assert response.status_code == 200
    assert response.json() == {"ok": True}
    assert captured == ["GET"]


@pytest.mark.parametrize(
    "method",
    [
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
    ],
)
def test_read_only_client_blocks_mutating_requests(
    method: str,
) -> None:
    """只读模式应在 transport 前阻止所有写方法。"""
    captured: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        captured.append(request.method)
        return httpx.Response(
            status_code=204,
            request=request,
        )

    with (
        APIClient(
            base_url="https://safe.local",
            read_only=True,
            transport=httpx.MockTransport(handler),
        ) as client,
        pytest.raises(
            ReadOnlyViolationError,
            match=f"只读模式禁止写请求: {method}",
        ) as exc_info,
    ):
        client.request(
            method,
            "/api/orders",
            json_body={
                "title": "forbidden-write",
            },
        )

    assert exc_info.value.method == method
    assert exc_info.value.url == "https://safe.local/api/orders"
    assert captured == []
