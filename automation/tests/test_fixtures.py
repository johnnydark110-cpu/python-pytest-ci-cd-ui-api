"""阶段一 fixture 用例：观察共享依赖与作用域生命周期。"""

import pytest

pytestmark = pytest.mark.regression


def test_first_case_receives_context(
    function_context: dict[str, str],
) -> None:
    """第一条用例应收到依赖注入的 function fixture。"""
    assert function_context == {
        "scope": "function",
        "suite_id": "local-suite",
    }


def test_second_case_receives_context(
    function_context: dict[str, str],
) -> None:
    """第二条用例应通过新创建的 function fixture 收到同一个会话标识。"""
    assert function_context["scope"] == "function"
    assert function_context["suite_id"] == "local-suite"
