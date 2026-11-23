"""环境分级与执行档位门禁测试。"""

import pytest

from config import (
    EnvironmentName,
    SuiteName,
    resolve_execution_profile,
)

pytestmark = pytest.mark.regression


@pytest.mark.parametrize(
    ("environment", "expected_suite", "expected_marker"),
    [
        ("dev", "full", None),
        ("staging", "regression", "regression"),
        ("prod", "smoke", "smoke"),
    ],
)
def test_environment_uses_safe_default_suite(
    environment: EnvironmentName,
    expected_suite: SuiteName,
    expected_marker: SuiteName | None,
) -> None:
    """每个环境应自动采用预先定义的安全档位。"""
    profile = resolve_execution_profile(environment)

    assert profile.environment == environment
    assert profile.suite == expected_suite
    assert profile.marker == expected_marker


@pytest.mark.parametrize(
    ("environment", "unsafe_suite"),
    [
        ("staging", "full"),
        ("prod", "regression"),
        ("prod", "full"),
    ],
)
def test_unsafe_environment_suite_combination_is_rejected(
    environment: EnvironmentName,
    unsafe_suite: SuiteName,
) -> None:
    """预发和线上不得执行不被允许的高风险档位。"""
    with pytest.raises(ValueError, match="不允许") as exc_info:
        resolve_execution_profile(
            environment,
            unsafe_suite,
        )

    assert unsafe_suite in str(exc_info.value)
