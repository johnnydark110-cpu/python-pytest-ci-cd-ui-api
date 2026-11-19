"""订单列表与表单页面的业务操作。"""

from __future__ import annotations

from playwright.sync_api import Locator, expect

from .base_page import BasePage


class OrderPage(BasePage):
    """封装订单新增、搜索、编辑和删除操作。"""

    ORDERS_PANEL = "orders-panel"
    ORDER_ITEM = "order-item"
    TITLE_INPUT = "order-title-input"
    AMOUNT_INPUT = "order-amount-input"
    STATUS_SELECT = "order-status-select"
    SUBMIT_BUTTON = "order-create-submit"
    SEARCH_INPUT = "order-search-input"
    SEARCH_BUTTON = "order-search-button"
    EDIT_BUTTON = "order-edit-button"
    DELETE_BUTTON = "order-delete-button"
    PAGE_INFO = "page-info"

    def open(self) -> None:
        """打开订单页面。"""
        self.goto("/")

    def wait_until_ready(self) -> None:
        """等待登录后的订单列表加载完成。"""
        expect(self.by_test_id(self.ORDERS_PANEL)).to_be_visible(
            timeout=self.timeout_ms,
        )
        expect(self.by_test_id(self.PAGE_INFO)).to_be_visible(
            timeout=self.timeout_ms,
        )

    def create_order(self, *, title: str, amount: float, status: str) -> Locator:
        """新增订单并等待对应订单行出现。"""
        self.fill(self.TITLE_INPUT, title)
        self.fill(self.AMOUNT_INPUT, str(amount))
        self.select_option(self.STATUS_SELECT, status)
        self.click(self.SUBMIT_BUTTON)

        return self.wait_for_order(
            title=title,
            amount=amount,
            status=status,
        )

    def search(self, keyword: str) -> None:
        """按标题关键字搜索订单。"""
        self.fill(self.SEARCH_INPUT, keyword)
        self.click(self.SEARCH_BUTTON)

    def order_rows(self, title: str) -> Locator:
        """按标题定位订单行。"""
        return self.by_test_id(self.ORDER_ITEM).filter(has_text=title)

    def wait_for_order(
        self,
        *,
        title: str,
        amount: float,
        status: str,
    ) -> Locator:
        """等待订单出现并校验标题、金额和状态。"""
        row = self.order_rows(title)

        expect(row).to_have_count(1, timeout=self.timeout_ms)
        expect(row).to_be_visible(timeout=self.timeout_ms)
        expect(row.locator("td").nth(1)).to_have_text(
            title,
            timeout=self.timeout_ms,
        )
        expect(row.locator("td").nth(2)).to_contain_text(
            str(amount),
            timeout=self.timeout_ms,
        )
        expect(row.locator("td").nth(3)).to_have_text(
            status,
            timeout=self.timeout_ms,
        )
        return row

    def edit_order(
        self,
        *,
        current_title: str,
        new_title: str,
        new_amount: float,
        new_status: str,
    ) -> Locator:
        """编辑已有订单并等待更新后的订单行出现。"""
        row = self.order_rows(current_title)
        expect(row).to_be_visible(timeout=self.timeout_ms)
        row.get_by_test_id(self.EDIT_BUTTON).click()

        expect(self.by_test_id(self.TITLE_INPUT)).to_have_value(
            current_title,
            timeout=self.timeout_ms,
        )
        expect(self.by_test_id(self.SUBMIT_BUTTON)).to_have_text(
            "保存修改",
            timeout=self.timeout_ms,
        )

        self.fill(self.TITLE_INPUT, new_title)
        self.fill(self.AMOUNT_INPUT, str(new_amount))
        self.select_option(self.STATUS_SELECT, new_status)
        self.click(self.SUBMIT_BUTTON)

        return self.wait_for_order(
            title=new_title,
            amount=new_amount,
            status=new_status,
        )

    def delete_order(self, title: str) -> None:
        """删除订单并自动接受浏览器确认框。"""
        row = self.order_rows(title)
        expect(row).to_be_visible(timeout=self.timeout_ms)

        self.page.once(
            "dialog",
            lambda dialog: dialog.accept(),
        )
        row.get_by_test_id(self.DELETE_BUTTON).click()

        self.wait_for_order_absent(title)

    def wait_for_order_absent(self, title: str) -> None:
        """等待指定标题的订单从列表中消失。"""
        expect(self.order_rows(title)).to_have_count(
            0,
            timeout=self.timeout_ms,
        )
