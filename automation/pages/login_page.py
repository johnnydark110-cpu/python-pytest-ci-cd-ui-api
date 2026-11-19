"""登录页面的业务操作。"""

from playwright.sync_api import expect

from .base_page import BasePage


class LoginPage(BasePage):
    """封装登录表单、登录成功和失败状态。"""

    AUTH_PANEL = "auth-panel"
    AUTH_TITLE = "auth-title"
    USERNAME_INPUT = "auth-username"
    PASSWORD_INPUT = "auth-password"
    SUBMIT_BUTTON = "auth-submit"
    AUTH_MESSAGE = "auth-message"
    ORDERS_PANEL = "orders-panel"
    USER_GREETING = "user-greeting"

    def open(self) -> None:
        """打开登录页并确认处于登录模式。"""
        self.goto("/")
        self.wait_for_visible(self.AUTH_PANEL)
        expect(self.by_test_id(self.AUTH_TITLE)).to_have_text(
            "登录", timeout=self.timeout_ms
        )

    def submit_credentials(
        self,
        username: str,
        password: str,
    ) -> None:
        """填写账号密码并提交登录表单。"""
        self.fill(self.USERNAME_INPUT, username)
        self.fill(self.PASSWORD_INPUT, password)
        self.click(self.SUBMIT_BUTTON)

    def wait_until_logged_in(self, username: str) -> None:
        """等待登录成功并确认订单面板显示。"""
        expect(self.by_test_id(self.ORDERS_PANEL)).to_be_visible(
            timeout=self.timeout_ms,
        )
        expect(self.by_test_id(self.AUTH_PANEL)).to_be_hidden(
            timeout=self.timeout_ms,
        )
        expect(self.by_test_id(self.USER_GREETING)).to_contain_text(
            username,
            timeout=self.timeout_ms,
        )

    def wait_for_login_error(self, message: str) -> None:
        """等待登录失败提示，并确认仍停留在登录页。"""
        expect(self.by_test_id(self.AUTH_MESSAGE)).to_have_text(
            message,
            timeout=self.timeout_ms,
        )
        expect(self.by_test_id(self.AUTH_PANEL)).to_be_visible(
            timeout=self.timeout_ms,
        )
        expect(self.by_test_id(self.ORDERS_PANEL)).to_be_hidden(
            timeout=self.timeout_ms,
        )
