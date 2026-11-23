"""自动化测试环境配置。"""

from .execution_profile import (
    ENVIRONMENT_POLICIES,
    EnvironmentName,
    ExecutionProfile,
    SuiteName,
    resolve_execution_profile,
)
from .settings import Settings

__all__ = [
    "ENVIRONMENT_POLICIES",
    "EnvironmentName",
    "ExecutionProfile",
    "Settings",
    "SuiteName",
    "resolve_execution_profile",
]
