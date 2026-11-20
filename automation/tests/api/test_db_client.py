"""SQLite 数据库校验与清理用例。"""

import pytest

from core import DBClient
from services import AuthService, OrderService
from utils import TestDataFactory

pytestmark = [
    pytest.mark.regression,
    pytest.mark.flaky(
        reruns=2,
        reruns_delay=1,
        only_rerun=["APITransportError"],
    ),
]


def test_db_client_removes_user_sessions_and_orders(
    auth_service: AuthService,
    db_client: DBClient,
    data_factory: TestDataFactory,
) -> None:
    """删除用户时应同时清理 session 和关联订单。"""
    user = data_factory.user()

    try:
        register_response = auth_service.register(
            username=user.username,
            password=user.password,
        )
        assert register_response.status_code == 201
        assert db_client.user_exists(user.username)

        token = auth_service.get_token(
            username=user.username,
            password=user.password,
        )
        assert db_client.session_exists(token)

        orders = OrderService(
            auth_service.api_client,
            token,
        )
        order_data = data_factory.order()
        create_response = orders.create_order(
            title=order_data.title,
            amount=order_data.amount,
            status=order_data.status,
        )
        assert create_response.status_code == 201
        order_id = create_response.json()["id"]
        assert db_client.order_exists(order_id)

        deleted = db_client.delete_user_by_username(user.username)

        assert deleted is True
        assert not db_client.user_exists(user.username)
        assert not db_client.session_exists(token)
        assert not db_client.order_exists(order_id)
    finally:
        db_client.delete_user_by_username(user.username)


def test_delete_missing_user_returns_false(
    db_client: DBClient,
    data_factory: TestDataFactory,
) -> None:
    """删除不存在的用户应安全返回 False。"""
    missing_user = data_factory.user()

    assert not db_client.user_exists(missing_user.username)
    assert not db_client.delete_user_by_username(missing_user.username)
