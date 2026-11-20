"""token 缓存、失效和刷新用例。"""

import pytest

from core import DBClient
from services import TokenManager

pytestmark = [
    pytest.mark.regression,
    pytest.mark.flaky(
        reruns=2,
        reruns_delay=1,
        only_rerun=["APITransportError"],
    ),
]


def test_token_manager_reuses_valid_cached_token(
    token_manager: TokenManager,
) -> None:
    """有效缓存存在时不应重复登录。"""
    first_token = token_manager.get_valid_token()
    second_token = token_manager.get_valid_token()

    assert first_token == second_token
    assert token_manager.cached_token == first_token
    assert token_manager.login_count == 1


def test_token_manager_refreshes_after_session_removed(
    token_manager: TokenManager,
    db_client: DBClient,
) -> None:
    """旧 session 删除后应检测失效并重新登录。"""
    first_token = token_manager.get_valid_token()

    assert token_manager.login_count == 1
    assert db_client.session_exists(first_token)

    assert db_client.delete_session(first_token) is True
    assert not db_client.session_exists(first_token)

    second_token = token_manager.get_valid_token()

    assert second_token != first_token
    assert token_manager.login_count == 2
    assert token_manager.cached_token == second_token
    assert db_client.session_exists(second_token)
