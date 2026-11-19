"""BasePage 导航、等待、交互和截图接线测试。"""

import pytest
from playwright.sync_api import Page

from pages import BasePage

pytestmark = pytest.mark.regression


def test_base_page_supports_core_ui_actions(
    page: Page,
    base_url: str,
) -> None:
    base_page = BasePage(page)

    response = base_page.goto("/")

    assert response is not None
    assert response.status == 200
    assert page.url.rstrip("/") == base_url.rstrip("/")
    assert page.title() == "订单管理系统"

    assert base_page.text("auth-title") == "登录"

    base_page.wait_for_visible("auth-panel")

    base_page.fill("auth-username", "base-page-demo")
    base_page.fill("auth-password", "secret123")

    assert base_page.by_test_id("auth-username").input_value() == "base-page-demo"
    assert base_page.by_test_id("auth-password").input_value() == "secret123"

    base_page.click("auth-switch")

    assert base_page.text("auth-title") == "注册"
    assert base_page.text("auth-switch") == "已有账号？去登录"

    screenshot_path = base_page.screenshot("base-page-wiring")

    assert screenshot_path.is_file()
    assert screenshot_path.suffix == ".png"
    assert screenshot_path.stat().st_size > 0
