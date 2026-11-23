"""UI 造数、API 校验与 UI 回显的混合用户旅程。"""

from __future__ import annotations

from pathlib import Path

import allure
import pytest
from playwright.sync_api import Page

from core import (
    DBClient,
    load_json_schema,
    validate_json_contract,
)
from pages import LoginPage, OrderPage
from services import OrderService
from utils import OrderData

pytestmark = [
    pytest.mark.regression,
    pytest.mark.serial,
]

SCHEMA_DIR = Path(__file__).resolve().parents[2] / "testdata" / "schemas"

ORDER_SCHEMA = load_json_schema(SCHEMA_DIR / "order.json")
ORDER_LIST_SCHEMA = load_json_schema(SCHEMA_DIR / "order_list.json")


@allure.feature("混合用户旅程")
@allure.story("UI 造数与 API 校验")
def test_ui_order_journey_is_visible_to_api_and_ui(
    page: Page,
    auth_user: dict[str, str],
    order_data: OrderData,
    order_service: OrderService,
    db_client: DBClient,
) -> None:
    """UI 创建的订单应能被 API 校验，并最终从 UI 和数据库中清理。"""
    login_page = LoginPage(page)
    order_page = OrderPage(page)

    created_order_id: int | None = None
    order_cleanup_confirmed = False

    try:
        with allure.step("通过 UI 登录测试用户"):
            login_page.open()
            login_page.submit_credentials(
                username=auth_user["username"],
                password=auth_user["password"],
            )
            login_page.wait_until_logged_in(
                auth_user["username"],
            )

        with allure.step("通过 UI 创建订单"):
            order_page.wait_until_ready()
            order_page.create_order(
                title=order_data.title,
                amount=order_data.amount,
                status=order_data.status,
            )

        with allure.step("通过 API 查询并校验订单"):
            list_response = order_service.list_orders(
                page=1,
                page_size=10,
                query=order_data.title,
            )

            assert list_response.status_code == 200, list_response.text

            list_body = list_response.json()
            validate_json_contract(
                list_body,
                ORDER_LIST_SCHEMA,
                label="订单列表响应",
            )

            assert list_body["total"] == 1
            assert len(list_body["items"]) == 1

            list_item = list_body["items"][0]
            created_order_id = list_item["id"]

            assert isinstance(created_order_id, int)
            assert list_item["title"] == order_data.title
            assert list_item["amount"] == pytest.approx(order_data.amount)
            assert list_item["status"] == order_data.status
            assert db_client.order_exists(created_order_id)

            detail_response = order_service.get_order(
                created_order_id,
            )

            assert detail_response.status_code == 200, detail_response.text

            detail_body = detail_response.json()
            validate_json_contract(
                detail_body,
                ORDER_SCHEMA,
                label="订单详情响应",
            )

            assert detail_body["id"] == created_order_id
            assert detail_body["title"] == order_data.title
            assert detail_body["amount"] == pytest.approx(order_data.amount)
            assert detail_body["status"] == order_data.status

        with allure.step("通过 UI 搜索并确认订单回显"):
            order_page.search(order_data.title)
            order_page.wait_for_order(
                title=order_data.title,
                amount=order_data.amount,
                status=order_data.status,
            )

        with allure.step("通过 API 删除订单并确认数据库无残留"):
            delete_response = order_service.delete_order(
                created_order_id,
            )

            assert delete_response.status_code == 204, delete_response.text
            order_cleanup_confirmed = True

            missing_response = order_service.get_order(
                created_order_id,
            )
            assert missing_response.status_code == 404
            assert not db_client.order_exists(created_order_id)

        with allure.step("通过 UI 确认订单已经消失"):
            order_page.search(order_data.title)
            order_page.wait_for_order_absent(
                order_data.title,
            )

    finally:
        if created_order_id is not None and not order_cleanup_confirmed:
            cleanup_response = order_service.delete_order(
                created_order_id,
            )
            assert cleanup_response.status_code in {204, 404}, (
                "异常收尾时订单清理失败: "
                f"{cleanup_response.status_code} {cleanup_response.text}"
            )
