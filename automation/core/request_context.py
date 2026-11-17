"""按测试收集 HTTP 请求响应历史。"""

from __future__ import annotations

from contextvars import ContextVar
from typing import Any

from .logger import redact_data

_REQUEST_HISTORY: ContextVar[list[dict[str, Any]] | None] = ContextVar(
    "request_history",
    default=None,
)


def start_request_history() -> None:
    """为当前测试创建独立的请求历史。"""
    _REQUEST_HISTORY.set([])


def stop_request_history() -> None:
    """测试结束后释放当前请求历史。"""
    _REQUEST_HISTORY.set(None)


def record_request_exchange(
    request_context: dict[str, Any],
    response_context: dict[str, Any],
) -> None:
    """脱敏后记录一次请求响应交换。"""
    history = _REQUEST_HISTORY.get()
    if history is None:
        return

    history.append(
        {
            "request": redact_data(request_context),
            "response": redact_data(response_context),
        }
    )


def get_request_history() -> list[dict[str, Any]]:
    """返回当前测试已经记录的请求响应历史副本。"""
    history = _REQUEST_HISTORY.get()
    return list(history) if history else []
