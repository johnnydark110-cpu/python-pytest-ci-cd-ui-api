"""trace_id 与流量染色请求头测试。"""

from __future__ import annotations

import httpx
import pytest

from core import (
    APIClient,
    get_request_history,
    get_trace_context,
    start_trace_context,
    stop_trace_context,
)

pytestmark = pytest.mark.regression


def test_trace_context_generates_unique_ids() -> None:
    """每次开始 trace 都应生成不同的 trace_id。"""
    first_token = start_trace_context(
        traffic_tag="automation.unit",
    )

    try:
        first = get_trace_context()

        assert first is not None
        assert first.traffic_tag == "automation.unit"
        assert len(first.trace_id) == 32
    finally:
        stop_trace_context(first_token)

    second_token = start_trace_context(
        traffic_tag="automation.unit",
    )

    try:
        second = get_trace_context()

        assert second is not None
        assert second.trace_id != first.trace_id
    finally:
        stop_trace_context(second_token)


def test_api_client_injects_trace_headers() -> None:
    """APIClient 应注入当前 trace，并阻止调用方覆盖。"""
    captured_headers: dict[str, str] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured_headers.update(request.headers)
        return httpx.Response(
            status_code=200,
            json={"ok": True},
            request=request,
        )

    token = start_trace_context(
        trace_id="trace-request-001",
        traffic_tag="automation.unit",
    )

    try:
        with APIClient(
            base_url="https://safe.local",
            read_only=True,
            transport=httpx.MockTransport(handler),
        ) as client:
            response = client.get(
                "/api/orders",
                headers={
                    "X-Trace-ID": "caller-cannot-override",
                    "X-Traffic-Tag": "manual",
                },
            )
    finally:
        stop_trace_context(token)

    assert response.status_code == 200
    assert captured_headers["x-trace-id"] == "trace-request-001"
    assert captured_headers["x-traffic-tag"] == "automation.unit"


def test_request_history_contains_trace_metadata() -> None:
    """请求历史应保存 trace_id 和 traffic_tag。"""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            status_code=200,
            json={"ok": True},
            request=request,
        )

    token = start_trace_context(
        trace_id="trace-history-001",
        traffic_tag="automation.history",
    )

    try:
        with APIClient(
            base_url="https://safe.local",
            read_only=True,
            transport=httpx.MockTransport(handler),
        ) as client:
            client.get("/api/orders")
    finally:
        stop_trace_context(token)

    history = get_request_history()
    assert history

    request_context = history[-1]["request"]
    assert request_context["trace_id"] == "trace-history-001"
    assert request_context["traffic_tag"] == "automation.history"
