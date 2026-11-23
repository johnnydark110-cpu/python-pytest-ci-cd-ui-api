"""Mock、Stub 与 MockTransport 单元测试。"""

from __future__ import annotations

import json
from typing import cast
from unittest.mock import Mock

import httpx
import pytest

from core import APIClient
from services import AuthService, TokenManager

pytestmark = pytest.mark.regression


def test_api_client_uses_mock_transport() -> None:
    """APIClient 应能在完全不访问网络时处理请求。"""
    captured: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["method"] = request.method
        captured["url"] = str(request.url)
        captured["authorization"] = request.headers["authorization"]
        captured["body"] = json.loads(request.content.decode("utf-8"))

        return httpx.Response(
            status_code=201,
            json={"id": 1, "name": "mock-order"},
            request=request,
        )

    transport = httpx.MockTransport(handler)

    with APIClient(
        base_url="https://mock.local",
        transport=transport,
    ) as client:
        response = client.post(
            "/api/orders",
            json_body={
                "title": "mock-order",
                "amount": 10.0,
            },
            headers={
                "Authorization": "Bearer mock-token",
            },
        )

    assert response.status_code == 201
    assert response.json() == {
        "id": 1,
        "name": "mock-order",
    }

    assert captured["method"] == "POST"
    assert captured["url"] == "https://mock.local/api/orders"
    assert captured["authorization"] == "Bearer mock-token"
    assert captured["body"] == {
        "title": "mock-order",
        "amount": 10.0,
    }


class StubAuthService:
    """只实现 TokenManager 所需鉴权方法的测试替身。"""

    def __init__(self, tokens: list[str]) -> None:
        self._tokens = iter(tokens)
        self.calls: list[tuple[str, str]] = []

    def get_token(
        self,
        *,
        username: str,
        password: str,
    ) -> str:
        self.calls.append((username, password))
        return next(self._tokens)


def test_token_manager_with_stub_auth_service() -> None:
    """Stub 应提供可控 token，并验证缓存和失效行为。"""
    stub = StubAuthService(tokens=["stub-token-1", "stub-token-2"])
    auth_service = cast(AuthService, stub)

    manager = TokenManager(
        auth_service,
        username="stub-user",
        password="stub-password",
        validator=lambda token: token == "stub-token-1",
    )

    first_token = manager.get_valid_token()
    cached_token = manager.get_valid_token()

    assert first_token == "stub-token-1"
    assert cached_token == "stub-token-1"
    assert manager.login_count == 1
    assert stub.calls == [
        ("stub-user", "stub-password"),
    ]

    manager.invalidate()
    refreshed_token = manager.get_valid_token()

    assert refreshed_token == "stub-token-2"
    assert manager.login_count == 2
    assert stub.calls == [
        ("stub-user", "stub-password"),
        ("stub-user", "stub-password"),
    ]


def test_token_manager_uses_mock_call_contract() -> None:
    """Mock 应验证 TokenManager 调用鉴权服务的次数与参数。"""
    auth_service = Mock(spec=AuthService)
    auth_service.get_token.side_effect = [
        "mock-token-1",
        "mock-token-2",
    ]

    manager = TokenManager(
        auth_service,
        username="mock-user",
        password="mock-password",
        validator=lambda token: token == "mock-token-1",
    )

    assert manager.get_valid_token() == "mock-token-1"
    assert manager.get_valid_token() == "mock-token-1"
    assert auth_service.get_token.call_count == 1

    assert manager.get_valid_token(force_refresh=True) == "mock-token-2"
    assert manager.login_count == 2
    assert auth_service.get_token.call_count == 2

    auth_service.get_token.assert_called_with(
        username="mock-user",
        password="mock-password",
    )
