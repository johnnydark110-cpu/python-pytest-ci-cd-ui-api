"""阶段一的框架冒烟用例。"""

import pytest

pytestmark = pytest.mark.smoke


def test_pytest_can_collect_and_run() -> None:
    """确认 pytest 能发现用例并执行普通断言。"""
    assert 2 + 2 == 4
