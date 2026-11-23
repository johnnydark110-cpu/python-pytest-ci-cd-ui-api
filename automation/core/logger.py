"""统一日志配置与敏感数据脱敏。"""

from __future__ import annotations

import json
import logging
from collections.abc import Mapping
from typing import Any

from .trace_context import get_trace_id

PACKAGE_LOGGER_NAME = "automation"
LOG_FORMAT = "%(asctime)s | %(levelname)s | trace=%(trace_id)s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
REDACTED_VALUE = "***REDACTED***"


class TraceIdFilter(logging.Filter):
    """向每条日志记录注入当前测试的 trace_id。"""

    def filter(self, record: logging.LogRecord) -> bool:
        record.trace_id = get_trace_id() or "-"
        return True


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


def _ensure_trace_filter(handler: logging.Handler) -> None:
    """确保 handler 只添加一次 trace 过滤器。"""
    if any(
        isinstance(existing_filter, TraceIdFilter)
        for existing_filter in handler.filters
    ):
        return

    handler.addFilter(TraceIdFilter())


def configure_logging(level: int | str = logging.INFO) -> None:
    """配置测试框架统一日志；重复调用不会添加重复 handler。"""
    package_logger = logging.getLogger(PACKAGE_LOGGER_NAME)
    package_logger.setLevel(level)
    package_logger.propagate = False

    if package_logger.handlers:
        for existing_handler in package_logger.handlers:
            _ensure_trace_filter(existing_handler)
        return

    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter(
            fmt=LOG_FORMAT,
            datefmt=DATE_FORMAT,
        )
    )
    _ensure_trace_filter(handler)
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


def format_log_data(value: Any) -> str:
    """先脱敏，再格式化为便于排错的多行 JSON。"""
    redacted = redact_data(value)
    return json.dumps(
        redacted,
        ensure_ascii=False,
        indent=2,
        default=str,
    )
