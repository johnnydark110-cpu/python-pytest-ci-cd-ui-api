"""Playwright 浏览器生命周期接线测试。"""

import pytest
from playwright.sync_api import Page

from core import BrowserManager

pytestmark = pytest.mark.regression


def test_page_fixture_opens_application_ui(
    page: Page,
    base_url: str,
) -> None:
    """page fixture 应能打开订单系统并定位稳定元素。"""
    response = page.goto("/", wait_until="domcontentloaded")

    assert response is not None
    assert response.status == 200
    assert page.url.rstrip("/") == base_url.rstrip("/")
    assert page.title() == "订单管理系统"
    assert page.get_by_test_id("auth-panel").is_visible()
    assert page.get_by_test_id("auth-username").is_visible()
    assert page.get_by_test_id("auth-password").is_visible()


def test_browser_contexts_keep_storage_isolated(
    browser_manager: BrowserManager,
    base_url: str,
) -> None:
    """两个 BrowserContext 不应共享 localStorage。"""
    first_context = browser_manager.new_context(
        base_url=base_url,
        ignore_https_errors=True,
    )
    second_context = browser_manager.new_context(
        base_url=base_url,
        ignore_https_errors=True,
    )

    try:
        first_page = first_context.new_page()
        first_page.goto("/", wait_until="domcontentloaded")
        first_page.evaluate("localStorage.setItem('browser-context-marker', 'set')")

        assert (
            first_page.evaluate("localStorage.getItem('browser-context-marker')")
            == "set"
        )

        second_page = second_context.new_page()
        second_page.goto("/", wait_until="domcontentloaded")

        assert (
            second_page.evaluate("localStorage.getItem('browser-context-marker')")
            is None
        )
    finally:
        first_context.close()
        second_context.close()
