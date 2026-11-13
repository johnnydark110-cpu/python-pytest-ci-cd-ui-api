"""阶段一基础用例：练习行为型命名和 pytest 断言。"""

import pytest

pytestmark = [
    pytest.mark.regression,
    pytest.mark.smoke
]


def test_strip_removes_surrounding_spaces() -> None:
    """字符串首尾空格应被移除。"""
    actual = "  smoke  ".strip()
    expected = "smoke"

    assert actual == expected


def test_order_status_is_allowed() -> None:
    """订单状态应存在于允许的状态集合中。"""
    allowed_statuses = {"pending", "paid", "shipped", "done", "canceled"}

    assert "paid" in allowed_statuses


def test_order_amount_is_positive() -> None:
    """订单金额应大于零。"""
    amount = 99.5

    assert amount > 0


def test_order_payload_matches_expected_value() -> None:
    """订单数据结构应与预期内容一致。"""
    order = {
        "id": 1,
        "title": "测试订单",
        "amount": 99.5,
        "status": "pending",
    }
    expected = {
        "id": 1,
        "title": "测试订单",
        "amount": 99.5,
        "status": "pending",
    }

    assert order == expected
