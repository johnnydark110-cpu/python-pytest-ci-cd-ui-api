"""使用 YAML 参数化驱动订单创建场景。"""

from pathlib import Path
from typing import Any

import allure
import pytest

from core import load_yaml_test_cases
from services import OrderService

pytestmark = [
    pytest.mark.regression,
    pytest.mark.flaky(
        reruns=2,
        reruns_delay=1,
        only_rerun=["APITransportError"],
    ),
]

DATA_PATH = Path(__file__).resolve().parents[2] / "testdata" / "orders.yaml"
ORDER_CREATE_CASES = load_yaml_test_cases(DATA_PATH)


@allure.feature("订单管理")
@allure.story("创建订单")
@pytest.mark.parametrize(
    "case",
    ORDER_CREATE_CASES,
    ids=[case["id"] for case in ORDER_CREATE_CASES],
)
def test_create_order_from_yaml_data(
    order_service: OrderService,
    case: dict[str, Any],
) -> None:
    """每组 YAML 数据应得到对应的创建结果。"""
    allure.dynamic.title(f"创建订单场景：{case['id']}")

    response = order_service.create_order(
        title=case["title"],
        amount=case["amount"],
        status=case["status"],
    )

    with allure.step("校验订单创建响应"):
        assert response.status_code == case["expected_status"], response.text

        if case["expected_status"] == 201:
            created = response.json()

            assert isinstance(created["id"], int)
            assert created["id"] > 0
            assert created["title"] == case["title"]
            assert created["amount"] == case["amount"]
            assert created["status"] == case["status"]
            assert isinstance(created["created_at"], str)
            assert created["created_at"]
        else:
            assert case["expected_status"] == 422

            detail = response.json()["detail"]
            assert isinstance(detail, list)
            assert detail

            invalid_fields = {
                error["loc"][-1]
                for error in detail
                if isinstance(error, dict) and error.get("loc")
            }
            assert case["expected_error_field"] in invalid_fields
