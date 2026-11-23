"""环境分级与 pytest 执行档位策略。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

EnvironmentName = Literal["dev", "staging", "prod"]
SuiteName = Literal["full", "regression", "smoke"]


@dataclass(frozen=True, slots=True)
class EnvironmentPolicy:
    """某个环境允许使用的默认档位和全部可用档位。"""

    default_suite: SuiteName
    allowed_suites: frozenset[SuiteName]


@dataclass(frozen=True, slots=True)
class ExecutionProfile:
    """一次测试执行最终采用的环境和档位。"""

    environment: EnvironmentName
    suite: SuiteName
    marker: SuiteName | None


ENVIRONMENT_POLICIES: dict[EnvironmentName, EnvironmentPolicy] = {
    "dev": EnvironmentPolicy(
        default_suite="full",
        allowed_suites=frozenset(
            {
                "full",
                "regression",
                "smoke",
            }
        ),
    ),
    "staging": EnvironmentPolicy(
        default_suite="regression",
        allowed_suites=frozenset(
            {
                "regression",
                "smoke",
            }
        ),
    ),
    "prod": EnvironmentPolicy(
        default_suite="smoke",
        allowed_suites=frozenset(
            {
                "smoke",
            }
        ),
    ),
}


def resolve_execution_profile(
    environment: EnvironmentName,
    requested_suite: SuiteName | None = None,
) -> ExecutionProfile:
    """解析环境和档位，并拒绝不安全的组合。"""
    policy = ENVIRONMENT_POLICIES.get(environment)

    if policy is None:
        raise ValueError(f"未知测试环境: {environment}")

    suite = requested_suite or policy.default_suite

    if suite not in policy.allowed_suites:
        allowed = "、".join(sorted(policy.allowed_suites))
        raise ValueError(
            f"{environment} 环境不允许 --suite={suite}；允许的档位为: {allowed}"
        )

    marker = None if suite == "full" else suite

    return ExecutionProfile(
        environment=environment,
        suite=suite,
        marker=marker,
    )
