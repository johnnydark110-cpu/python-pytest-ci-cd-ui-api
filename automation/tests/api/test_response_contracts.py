"""API 响应 JSON Schema 契约测试。"""

from pathlib import Path

import pytest

from core import load_json_schema, validate_json_contract
from services import AuthService, OrderService
from utils import OrderData

pytestmark = [
    pytest.mark.regression,
    pytest.mark.flaky(
        reruns=2,
        reruns_delay=1,
        only_rerun=["APITransportError"],
    ),
]

SCHEMA_DIR = Path(__file__).resolve().parents[2] / "testdata" / "schemas"

AUTH_RESPONSE_SCHEMA = load_json_schema(SCHEMA_DIR / "auth_response.json")
ORDER_SCHEMA = load_json_schema(SCHEMA_DIR / "order.json")
ORDER_LIST_SCHEMA = load_json_schema(SCHEMA_DIR / "order_list.json")


def test_auth_response_matches_contract(
    auth_service: AuthService,
    auth_user: dict[str, str],
) -> None:
    """注册响应应符合鉴权响应 schema。"""
    response = auth_service.register(
        username=auth_user["username"],
        password=auth_user["password"],
    )

    assert response.status_code == 201
    validate_json_contract(
        response.json(),
        AUTH_RESPONSE_SCHEMA,
        label="注册响应",
    )


def test_order_response_matches_contract(
    created_order: tuple[OrderData, dict],
) -> None:
    """创建订单响应应符合订单 schema。"""
    _, created = created_order

    validate_json_contract(
        created,
        ORDER_SCHEMA,
        label="订单响应",
    )


def test_order_list_matches_contract(
    created_order: tuple[OrderData, dict],
    order_service: OrderService,
) -> None:
    """订单列表响应应符合分页列表 schema。"""
    expected, _ = created_order

    response = order_service.list_orders(
        page=1,
        page_size=10,
        query=expected.title,
    )

    assert response.status_code == 200
    validate_json_contract(
        response.json(),
        ORDER_LIST_SCHEMA,
        label="订单列表响应",
    )


def test_contract_rejects_changed_field_type() -> None:
    """订单金额变成字符串时应被契约校验捕获。"""
    valid_order = {
        "id": 1,
        "title": "契约校验订单",
        "amount": 99.5,
        "status": "pending",
        "created_at": "2026-11-20 12:00:00",
    }

    validate_json_contract(
        valid_order,
        ORDER_SCHEMA,
        label="合法订单响应",
    )

    changed_order = {
        **valid_order,
        "amount": "99.5",
    }

    with pytest.raises(AssertionError, match="amount"):
        validate_json_contract(
            changed_order,
            ORDER_SCHEMA,
            label="变更订单响应",
        )
