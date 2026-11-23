"""按测试隔离的 trace_id 与流量标签上下文。"""

from __future__ import annotations

from contextvars import ContextVar, Token
from dataclasses import dataclass
from uuid import uuid4

TRACE_ID_HEADER = "X-Trace-ID"
TRAFFIC_TAG_HEADER = "X-Traffic-Tag"


@dataclass(frozen=True, slots=True)
class TraceContext:
    """当前测试使用的链路标识和流量标签。"""

    trace_id: str
    traffic_tag: str

    @property
    def headers(self) -> dict[str, str]:
        """返回注入到 API 和浏览器请求中的染色头。"""
        return {
            TRACE_ID_HEADER: self.trace_id,
            TRAFFIC_TAG_HEADER: self.traffic_tag,
        }


_TRACE_CONTEXT: ContextVar[TraceContext | None] = ContextVar(
    "trace_context",
    default=None,
)


def start_trace_context(
    *,
    traffic_tag: str,
    trace_id: str | None = None,
) -> Token[TraceContext | None]:
    """为当前测试创建 trace 上下文，并返回用于恢复的 token。"""
    normalized_tag = traffic_tag.strip()
    if not normalized_tag:
        raise ValueError("traffic_tag 不能为空")

    normalized_trace_id = (trace_id or uuid4().hex).strip()
    if not normalized_trace_id:
        raise ValueError("trace_id 不能为空")

    return _TRACE_CONTEXT.set(
        TraceContext(
            trace_id=normalized_trace_id,
            traffic_tag=normalized_tag,
        )
    )


def stop_trace_context(
    token: Token[TraceContext | None],
) -> None:
    """恢复进入当前 trace 上下文前的状态。"""
    _TRACE_CONTEXT.reset(token)


def get_trace_context() -> TraceContext | None:
    """返回当前测试的 trace 上下文。"""
    return _TRACE_CONTEXT.get()


def get_trace_id() -> str | None:
    """返回当前测试的 trace_id。"""
    context = get_trace_context()
    return context.trace_id if context is not None else None
