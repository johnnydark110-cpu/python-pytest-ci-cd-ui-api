"""pytest 的共享 fixture 入口。"""

from collections.abc import Iterator

import pytest


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
