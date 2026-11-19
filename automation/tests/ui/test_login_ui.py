"""登录页面 UI 成功与失败用例。"""

import pytest

from pages import LoginPage

pytestmark = pytest.mark.regression


def test_ui_login_success_shows_orders_panel(
    login_page: LoginPage,
    auth_user: dict[str, str],
    token: str,
) -> None:
    """已注册用户应能通过 UI 登录并进入订单面板。"""
    assert token

    login_page.open()
    login_page.submit_credentials(
        username=auth_user["username"], password=auth_user["password"]
    )

    login_page.wait_until_logged_in(auth_user["username"])

    assert login_page.text("user-greeting") == (
        f"你好，{auth_user['username']}（user）"
    )


def test_ui_login_rejects_wrong_password(
    login_page: LoginPage,
    auth_user: dict[str, str],
    token: str,
) -> None:
    """错误密码应显示明确提示且不进入订单面板。"""
    assert token

    login_page.open()
    login_page.submit_credentials(
        username=auth_user["username"],
        password="wrong-password",
    )
    login_page.wait_for_login_error(
        "用户名或密码错误",
    )
