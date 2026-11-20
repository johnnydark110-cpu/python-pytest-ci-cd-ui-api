"""订单 CRUD、分页搜索、参数校验与用户隔离用例。"""

from typing import Any
from uuid import uuid4

import pytest

from core import APIClient
from services import AuthService, OrderService

pytestmark = [
    pytest.mark.regression,
    pytest.mark.flaky(
        reruns=2,
        reruns_delay=1,
        only_rerun=["APITransportError"],
    ),
]


def _create_valid_order(
    order_service: OrderService,
    *,
    title: str,
    amount: float = 99.5,
    status: str = "pending",
) -> dict[str, Any]:
    """创建一条有效订单，并返回响应 JSON。"""
    response = order_service.create_order(
        title=title,
        amount=amount,
        status=status,
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_create_order_returns_created_order(
    order_service: OrderService,
) -> None:
    """创建订单应返回 201 和完整订单字段。"""
    title = f"订单-{uuid4().hex[:8]}"

    created = _create_valid_order(
        order_service,
        title=title,
    )

    assert isinstance(created["id"], int)
    assert created["id"] > 0
    assert created["title"] == title
    assert created["amount"] == 99.5
    assert created["status"] == "pending"
    assert isinstance(created["created_at"], str)
    assert created["created_at"]


def test_get_order_returns_owned_order(
    order_service: OrderService,
) -> None:
    """当前用户应能查询自己创建的订单详情。"""
    title = f"详情订单-{uuid4().hex[:8]}"
    created = _create_valid_order(
        order_service,
        title=title,
        amount=88.8,
        status="paid",
    )

    response = order_service.get_order(created["id"])

    assert response.status_code == 200
    detail = response.json()
    assert detail["id"] == created["id"]
    assert detail["title"] == title
    assert detail["amount"] == 88.8
    assert detail["status"] == "paid"
    assert detail["created_at"] == created["created_at"]


def test_list_orders_supports_search_and_pagination(
    order_service: OrderService,
) -> None:
    """订单列表应支持标题搜索和分页。"""
    prefix = f"search-{uuid4().hex[:6]}"
    first = _create_valid_order(
        order_service,
        title=f"{prefix}-alpha",
    )
    second = _create_valid_order(
        order_service,
        title=f"{prefix}-beta",
    )

    first_page_response = order_service.list_orders(
        page=1,
        page_size=1,
        query=prefix,
    )

    assert first_page_response.status_code == 200
    first_page = first_page_response.json()
    assert first_page["total"] == 2
    assert first_page["page"] == 1
    assert first_page["page_size"] == 1
    assert len(first_page["items"]) == 1
    assert prefix in first_page["items"][0]["title"]

    second_page_response = order_service.list_orders(
        page=2,
        page_size=1,
        query=prefix,
    )

    assert second_page_response.status_code == 200
    second_page = second_page_response.json()
    assert second_page["total"] == 2
    assert second_page["page"] == 2
    assert len(second_page["items"]) == 1
    assert prefix in second_page["items"][0]["title"]

    first_page_id = first_page["items"][0]["id"]
    second_page_id = second_page["items"][0]["id"]
    assert first_page_id != second_page_id
    assert {first_page_id, second_page_id} == {
        first["id"],
        second["id"],
    }


def test_update_order_changes_only_requested_fields(
    order_service: OrderService,
) -> None:
    """修改订单时未提供的字段应保持原值。"""
    original_title = f"待修改订单-{uuid4().hex[:8]}"
    created = _create_valid_order(
        order_service,
        title=original_title,
        amount=50.0,
        status="pending",
    )

    response = order_service.update_order(
        created["id"],
        amount=123.45,
        status="shipped",
    )

    assert response.status_code == 200
    updated = response.json()
    assert updated["id"] == created["id"]
    assert updated["title"] == original_title
    assert updated["amount"] == 123.45
    assert updated["status"] == "shipped"
    assert updated["created_at"] == created["created_at"]


def test_delete_order_removes_resource(
    order_service: OrderService,
) -> None:
    """删除成功返回 204，之后查询应返回 404。"""
    title = f"待删除订单-{uuid4().hex[:8]}"
    created = _create_valid_order(
        order_service,
        title=title,
    )

    delete_response = order_service.delete_order(created["id"])

    assert delete_response.status_code == 204
    assert delete_response.content == b""

    missing_response = order_service.get_order(created["id"])

    assert missing_response.status_code == 404
    assert missing_response.json()["detail"] == "订单不存在"


@pytest.mark.parametrize(
    "amount",
    [0, -1.0],
    ids=["zero", "negative"],
)
def test_create_order_rejects_non_positive_amount(
    order_service: OrderService,
    amount: float,
) -> None:
    """金额为零或负数时应返回参数校验错误。"""
    response = order_service.create_order(
        title=f"非法金额-{uuid4().hex[:8]}",
        amount=amount,
    )

    assert response.status_code == 422
    detail = response.json()["detail"]
    assert isinstance(detail, list)

    invalid_fields = {
        error["loc"][-1]
        for error in detail
        if isinstance(error, dict) and error.get("loc")
    }
    assert "amount" in invalid_fields


def test_create_order_rejects_invalid_status(
    order_service: OrderService,
) -> None:
    """不在允许集合内的订单状态应返回 422。"""
    response = order_service.create_order(
        title=f"非法状态-{uuid4().hex[:8]}",
        amount=10.0,
        status="unknown",
    )

    assert response.status_code == 422
    detail = response.json()["detail"]
    assert isinstance(detail, list)

    invalid_fields = {
        error["loc"][-1]
        for error in detail
        if isinstance(error, dict) and error.get("loc")
    }
    assert "status" in invalid_fields


def test_user_cannot_access_another_users_order(
    api_client: APIClient,
    auth_service: AuthService,
    order_service: OrderService,
) -> None:
    """不同用户之间不能读取或列出对方订单。"""
    first_user_order = _create_valid_order(
        order_service,
        title=f"用户隔离-{uuid4().hex[:8]}",
    )

    second_username = f"api_{uuid4().hex[:10]}"
    second_password = "secret123"
    register_response = auth_service.register(
        username=second_username,
        password=second_password,
    )
    assert register_response.status_code == 201

    second_token = auth_service.get_token(
        username=second_username,
        password=second_password,
    )
    second_user_orders = OrderService(api_client, second_token)

    list_response = second_user_orders.list_orders()
    assert list_response.status_code == 200
    assert list_response.json()["total"] == 0
    assert list_response.json()["items"] == []

    detail_response = second_user_orders.get_order(first_user_order["id"])
    assert detail_response.status_code == 404
    assert detail_response.json()["detail"] == "订单不存在"
