"""订单页面 UI 新增、搜索、修改和删除闭环。"""

from uuid import uuid4

import pytest

from pages import LoginPage, OrderPage

pytestmark = [
    pytest.mark.regression,
    pytest.mark.serial,
]


def test_order_ui_crud_flow(
    login_page: LoginPage,
    order_page: OrderPage,
    auth_user: dict[str, str],
    token: str,
) -> None:
    """UI 应完成订单新增、搜索、修改和删除。"""
    assert token

    login_page.open()
    login_page.submit_credentials(
        username=auth_user["username"],
        password=auth_user["password"],
    )
    login_page.wait_until_logged_in(
        auth_user["username"],
    )

    order_page.open()
    order_page.wait_until_ready()

    prefix = f"ui-order-{uuid4().hex[:8]}"
    original_title = f"{prefix}-original"
    updated_title = f"{prefix}-updated"

    order_page.create_order(
        title=original_title,
        amount=99.5,
        status="pending",
    )

    order_page.search(prefix)
    order_page.wait_for_order(
        title=original_title,
        amount=99.5,
        status="pending",
    )

    order_page.edit_order(
        current_title=original_title,
        new_title=updated_title,
        new_amount=123.45,
        new_status="paid",
    )

    order_page.wait_for_order(
        title=updated_title,
        amount=123.45,
        status="paid",
    )

    order_page.delete_order(updated_title)
    order_page.wait_for_order_absent(updated_title)
