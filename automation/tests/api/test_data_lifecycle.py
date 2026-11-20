"""fixture 动态数据准备与清理用例。"""

import pytest

from services import OrderService
from utils import OrderData

pytestmark = [
    pytest.mark.regression,
    pytest.mark.flaky(
        reruns=2,
        reruns_delay=1,
        only_rerun=["APITransportError"],
    ),
]


def test_created_order_fixture_persists_generated_data(
    created_order: tuple[OrderData, dict],
    order_service: OrderService,
) -> None:
    """已创建订单 fixture 应把动态数据真实写入系统。"""
    expected, created = created_order

    response = order_service.get_order(created["id"])

    assert response.status_code == 200
    detail = response.json()
    assert detail["id"] == created["id"]
    assert detail["title"] == expected.title
    assert detail["amount"] == expected.amount
    assert detail["status"] == expected.status
    assert detail["created_at"] == created["created_at"]


def test_created_order_search_is_isolated(
    created_order: tuple[OrderData, dict],
    order_service: OrderService,
) -> None:
    """当前测试只应搜索到自己的动态订单。"""
    expected, created = created_order

    response = order_service.list_orders(
        query=expected.title,
        page=1,
        page_size=10,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert len(body["items"]) == 1
    assert body["items"][0]["id"] == created["id"]
    assert body["items"][0]["title"] == expected.title
