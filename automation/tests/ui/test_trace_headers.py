"""浏览器请求的 trace 与流量染色测试。"""

import pytest
from playwright.sync_api import Page

from core import get_trace_context

pytestmark = pytest.mark.regression


def test_browser_requests_include_trace_headers(
    page: Page,
    base_url: str,
) -> None:
    """Playwright 请求应携带当前测试的染色头。"""
    captured_headers: dict[str, str] = {}
    expected_url = base_url.rstrip("/")

    def capture_request(request) -> None:
        if request.url.rstrip("/") == expected_url:
            captured_headers.update(request.headers)

    page.on("request", capture_request)
    page.goto("/", wait_until="domcontentloaded")

    trace = get_trace_context()

    assert trace is not None
    assert captured_headers["x-trace-id"] == trace.trace_id
    assert captured_headers["x-traffic-tag"] == trace.traffic_tag
