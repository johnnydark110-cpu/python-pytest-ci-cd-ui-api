"""pytest 的共享 fixture 入口。"""
import logging
from collections.abc import Iterator
from os import getenv
from uuid import uuid4

import pytest

from core import APIClient, configure_logging
from services import AuthService, OrderService


@pytest.fixture(scope="session")
def session_context() -> Iterator[dict[str, str]]:
    """整个测试会话只创建一次的共享上下文。"""
    print("\n[fixture setup] session_context")
    yield {"scope": "session", "suite_id": "local-suite"}
    print("[fixture teardown] session_context")


@pytest.fixture(scope="function")
def function_context(
        session_context: dict[str, str],
) -> Iterator[dict[str, str]]:
    """每条测试函数独立创建并销毁的上下文。"""
    print("[fixture setup] function_context")
    yield {
        "scope": "function",
        "suite_id": session_context["suite_id"],
    }
    print("[fixture teardown] function_context")


@pytest.fixture(scope="session")
def base_url() -> str:
    """提供当前测试环境的基础url"""
    return getenv("API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")


@pytest.fixture(scope="session")
def api_client(base_url: str) -> Iterator[APIClient]:
    """整个测试会话只共享一个HTTP客户端"""
    configure_logging(logging.INFO)

    with APIClient(base_url=base_url) as client:
        yield client


@pytest.fixture(scope="session")
def auth_service(api_client: APIClient) -> AuthService:
    """共享无状态的鉴权服务。"""
    return AuthService(api_client)


@pytest.fixture(scope="function")
def auth_user() -> dict[str, str]:
    suffix = uuid4().hex[:10]
    return {
        "username": f"api_{suffix}",
        "password": "secret123",
    }


@pytest.fixture(scope="function")
def token(
        auth_service: AuthService,
        auth_user: dict[str, str],
) -> str:
    """为当前测试创建独立用户并登录取得 token。"""

    register_response = auth_service.register(
        username=auth_user["username"],
        password=auth_user["password"],
    )
    assert register_response.status_code == 201, register_response.text

    return auth_service.get_token(
        username=auth_user["username"],
        password=auth_user["password"],
    )


@pytest.fixture(scope="function")
def order_service(
        api_client: APIClient,
        token: str
) -> OrderService:
    return OrderService(api_client, token)
