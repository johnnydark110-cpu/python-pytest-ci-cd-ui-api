"""鉴权接口的成功、失败与 token 有效性用例。"""

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


def test_register_returns_authenticated_user(
    auth_service: AuthService,
    auth_user: dict[str, str],
) -> None:
    """注册成功应返回用户信息和可用 token。"""
    response = auth_service.register(
        username=auth_user["username"],
        password=auth_user["password"],
    )

    assert response.status_code == 201
    body = response.json()
    assert body["username"] == auth_user["username"]
    assert body["role"] == "user"
    assert isinstance(body["token"], str)
    assert len(body["token"]) == 64
    assert "password" not in body


def test_register_rejects_duplicate_username(
    auth_service: AuthService,
    auth_user: dict[str, str],
) -> None:
    """相同用户名第二次注册应返回 409。"""
    first_response = auth_service.register(
        username=auth_user["username"],
        password=auth_user["password"],
    )
    assert first_response.status_code == 201

    duplicate_response = auth_service.register(
        username=auth_user["username"],
        password=auth_user["password"],
    )

    assert duplicate_response.status_code == 409
    assert duplicate_response.json()["detail"] == "用户名已存在"


def test_login_returns_token(
    auth_service: AuthService,
    auth_user: dict[str, str],
) -> None:
    """已注册用户登录应返回用户信息和 token。"""
    register_response = auth_service.register(
        username=auth_user["username"],
        password=auth_user["password"],
    )
    assert register_response.status_code == 201

    login_response = auth_service.login(
        username=auth_user["username"],
        password=auth_user["password"],
    )

    assert login_response.status_code == 200
    body = login_response.json()
    assert body["username"] == auth_user["username"]
    assert body["role"] == "user"
    assert isinstance(body["token"], str)
    assert len(body["token"]) == 64


def test_login_rejects_wrong_password(
    auth_service: AuthService,
    auth_user: dict[str, str],
) -> None:
    """密码错误应返回 401 和明确错误信息。"""
    register_response = auth_service.register(
        username=auth_user["username"],
        password=auth_user["password"],
    )
    assert register_response.status_code == 201

    login_response = auth_service.login(
        username=auth_user["username"],
        password="wrong-password",
    )

    assert login_response.status_code == 401
    assert login_response.json()["detail"] == "用户名或密码错误"


def test_register_rejects_invalid_payload(
    auth_service: AuthService,
) -> None:
    """过短用户名和密码应触发 FastAPI 参数校验。"""
    response = auth_service.register(
        username="ab",
        password="123",
    )

    assert response.status_code == 422
    detail = response.json()["detail"]
    assert isinstance(detail, list)
    assert detail

    invalid_fields = {
        error["loc"][-1]
        for error in detail
        if isinstance(error, dict) and error.get("loc")
    }
    assert {"username", "password"} <= invalid_fields

    for error in detail:
        assert error.get("msg")


def test_token_allows_order_access(
    order_service: OrderService,
) -> None:
    """token fixture 取得的 token 应能访问受保护订单接口。"""
    response = order_service.list_orders(
        page=1,
        page_size=1,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["page"] == 1
    assert body["page_size"] == 1


def test_invalid_token_is_rejected(
    api_client: APIClient,
) -> None:
    """无效 token 访问订单接口应返回 401。"""
    orders = OrderService(
        api_client,
        "invalid-token",
    )

    response = orders.list_orders()

    assert response.status_code == 401
    assert response.json()["detail"] == "登录已失效，请重新登录"
