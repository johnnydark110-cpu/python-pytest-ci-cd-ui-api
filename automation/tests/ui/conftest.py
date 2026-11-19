"""UI 测试共享 fixture。"""

import pytest
from playwright.sync_api import Page

from pages import LoginPage, OrderPage


@pytest.fixture(scope="function")
def login_page(page: Page) -> LoginPage:
    """为每条测试创建独立的登录页面对象。"""
    return LoginPage(page)


@pytest.fixture(scope="function")
def order_page(page: Page) -> OrderPage:
    """为每条测试创建独立的订单页面对象。"""
    return OrderPage(page)
