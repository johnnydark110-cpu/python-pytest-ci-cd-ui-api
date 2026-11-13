"""统一日志配置与敏感数据脱敏。"""
import logging
from collections.abc import Mapping
from typing import Any

PACKAGE_LOGGER_NAME = "automation"
LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
REDACTED_VALUE = "***REDACTED***"

_SENSITIVE_KEYS = frozenset(
    {
        "authorization",
        "cookie",
        "set-cookie",
        "token",
        "access_token",
        "refresh_token",
        "password",
        "api_key",
        "x-api-key",
    }
)


def configure_logging(level: int | str = logging.INFO) -> None:
    package_logger = logging.getLogger(PACKAGE_LOGGER_NAME)
    package_logger.setLevel(level)
    package_logger.propagate = False

    if package_logger.handlers:
        return

    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter(
            fmt=LOG_FORMAT,
            datefmt=DATE_FORMAT,
        )
    )
    package_logger.addHandler(handler)


def get_logger(name: str) -> logging.Logger:
    """获取 automation 命名空间下按模块区分的 logger。"""
    if name == PACKAGE_LOGGER_NAME:
        full_name = PACKAGE_LOGGER_NAME
    elif name.startswith(f"{PACKAGE_LOGGER_NAME}."):
        full_name = name
    else:
        full_name = f"{PACKAGE_LOGGER_NAME}.{name}"

    return logging.getLogger(full_name)


def redact_data(value: Any) -> Any:
    """递归替换字典、列表和元组中的敏感字段值。"""
    if isinstance(value, Mapping):
        return {
            key: (
                REDACTED_VALUE
                if str(key).lower() in _SENSITIVE_KEYS
                else redact_data(item)
            )
            for key, item in value.items()
        }

    if isinstance(value, list):
        return [redact_data(item) for item in value]

    if isinstance(value, tuple):
        return tuple(redact_data(item) for item in value)

    return value
