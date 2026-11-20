"""动态测试数据生成器单元测试。"""

import pytest

from utils import (
    ORDER_STATUSES,
    TestDataFactory,
)

pytestmark = pytest.mark.regression


def test_user_data_is_valid_and_unique() -> None:
    """批量用户数据应合法且用户名不重复。"""
    factory = TestDataFactory()
    users = [factory.user() for _ in range(100)]

    assert len({user.username for user in users}) == 100

    for user in users:
        assert 3 <= len(user.username) <= 32
        assert 6 <= len(user.password) <= 64
        assert user.password not in repr(user)


def test_order_data_is_valid_and_unique() -> None:
    """批量订单数据应合法且默认标题不重复。"""
    factory = TestDataFactory()
    orders = [factory.order() for _ in range(100)]

    assert len({order.title for order in orders}) == 100

    for order in orders:
        assert 1 <= len(order.title) <= 100
        assert order.amount > 0
        assert order.status in ORDER_STATUSES


def test_order_data_supports_overrides_and_rejects_invalid_values() -> None:
    """显式字段应生效，非法金额和状态应提前报错。"""
    factory = TestDataFactory()

    order = factory.order(
        title="指定标题订单",
        amount=88.88,
        status="paid",
    )

    assert order.title == "指定标题订单"
    assert order.amount == 88.88
    assert order.status == "paid"

    with pytest.raises(
        ValueError,
        match="订单金额必须大于 0",
    ):
        factory.order(amount=0)

    with pytest.raises(
        ValueError,
        match="不支持的订单状态",
    ):
        factory.order(status="unknown")
