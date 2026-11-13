"""阶段一参数化用例：用同一测试逻辑驱动多组数据。"""

import pytest

pytestmark = pytest.mark.regression


@pytest.mark.parametrize(
    ("title", "amount", "expected_valid"),
    [
        ("正常订单", 99.5, True),
        ("最小正金额", 0.01, True),
        ("   ", 99.5, False),
        ("零金额", 0, False),
        ("负金额", -1, False),
    ],
    ids=[
        "normal-order",
        "minimum-positive-amount",
        "blank-title",
        "zero-amount",
        "negative-amount",
    ]
)
def test_order_candidate_validation(
        title: str,
        amount: float,
        expected_valid: bool
) -> None:
    is_valid = bool(title.strip()) and amount > 0
    assert is_valid is expected_valid
