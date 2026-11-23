"""失败分类、known_flaky 元数据和重试结果汇总。"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Literal

from .exceptions import (
    APITransportError,
    AutomationError,
    CircuitOpenError,
    ReadOnlyViolationError,
)

FailureCategory = Literal[
    "environment",
    "configuration",
    "product_assertion",
    "framework_or_test",
    "unknown",
]


@dataclass(frozen=True, slots=True)
class FailureClassification:
    """一次失败的初步分类和分诊建议。"""

    category: FailureCategory
    exception_type: str
    reason: str
    triage: str

    def to_dict(self) -> dict[str, str]:
        """转换为可直接写入 JSON 的字典。"""
        return {
            "category": self.category,
            "exception_type": self.exception_type,
            "reason": self.reason,
            "triage": self.triage,
        }


@dataclass(frozen=True, slots=True)
class KnownFlakyPolicy:
    """known_flaky marker 的规范化元数据。"""

    issue: str
    owner: str
    expires: str
    reason: str

    def to_dict(self) -> dict[str, str]:
        """转换为可直接写入 JSON 的字典。"""
        return {
            "issue": self.issue,
            "owner": self.owner,
            "expires": self.expires,
            "reason": self.reason,
        }


def classify_failure(exception: BaseException) -> FailureClassification:
    """根据异常类型给出失败初始分类。"""
    exception_type = type(exception).__name__
    message = str(exception).splitlines()[0].strip()
    reason = message[:300] if message else exception_type

    if isinstance(exception, (APITransportError, CircuitOpenError)):
        return FailureClassification(
            category="environment",
            exception_type=exception_type,
            reason=reason,
            triage="检查被测系统、网络、DNS、代理和熔断状态",
        )

    exception_module = type(exception).__module__

    if exception_type in {
        "TimeoutError",
        "TargetClosedError",
    } and exception_module.startswith("playwright."):
        return FailureClassification(
            category="environment",
            exception_type=exception_type,
            reason=reason,
            triage="检查页面加载、浏览器进程和前端服务状态",
        )

    if isinstance(exception, ReadOnlyViolationError):
        return FailureClassification(
            category="configuration",
            exception_type=exception_type,
            reason=reason,
            triage="检查环境 read_only、suite 和写操作配置",
        )

    if isinstance(exception, AssertionError):
        return FailureClassification(
            category="product_assertion",
            exception_type=exception_type,
            reason=reason,
            triage="对比接口契约、页面行为和测试期望，判断产品缺陷或错误断言",
        )

    if isinstance(exception, AutomationError):
        return FailureClassification(
            category="framework_or_test",
            exception_type=exception_type,
            reason=reason,
            triage="检查自动化框架封装、fixture 和测试代码",
        )

    if isinstance(
        exception,
        (
            NameError,
            TypeError,
            AttributeError,
            KeyError,
            ImportError,
        ),
    ):
        return FailureClassification(
            category="framework_or_test",
            exception_type=exception_type,
            reason=reason,
            triage="修复测试代码、页面对象、模型或依赖导入",
        )

    return FailureClassification(
        category="unknown",
        exception_type=exception_type,
        reason=reason,
        triage="查看完整堆栈和 trace_id 后人工归类",
    )


def validate_known_flaky_metadata(
    *,
    issue: object,
    owner: object,
    expires: object,
    reason: object,
    today: date | None = None,
) -> KnownFlakyPolicy:
    """校验 known_flaky 必填字段和过期时间。"""
    normalized = {
        "issue": str(issue).strip() if issue is not None else "",
        "owner": str(owner).strip() if owner is not None else "",
        "expires": str(expires).strip() if expires is not None else "",
        "reason": str(reason).strip() if reason is not None else "",
    }

    for field_name, value in normalized.items():
        if not value:
            raise ValueError(f"known_flaky 缺少必填字段: {field_name}")

    try:
        expires_on = date.fromisoformat(normalized["expires"])
    except ValueError as exc:
        raise ValueError("known_flaky.expires 必须是 YYYY-MM-DD 日期") from exc

    effective_today = today or date.today()

    if expires_on < effective_today:
        raise ValueError(
            f"known_flaky 已过期: {normalized['expires']}，"
            "请修复测试或更新 issue 后延长期限"
        )

    return KnownFlakyPolicy(**normalized)


class FlakyAttemptLedger:
    """收集 call 阶段结果并汇总 flaky 状态。"""

    def __init__(self) -> None:
        self._events: dict[str, list[dict[str, Any]]] = {}

    def record(
        self,
        *,
        nodeid: str,
        outcome: str,
        when: str,
        classification: dict[str, Any] | None = None,
        known_flaky: dict[str, Any] | None = None,
    ) -> None:
        """记录一次有意义的结果事件。"""
        if when != "call" and outcome not in {"failed", "rerun"}:
            return

        event: dict[str, Any] = {
            "outcome": outcome,
            "when": when,
        }

        if classification is not None:
            event["classification"] = classification

        if known_flaky is not None:
            event["known_flaky"] = known_flaky

        self._events.setdefault(nodeid, []).append(event)

    def build(self) -> dict[str, Any]:
        """生成按测试节点汇总的 flaky 报告。"""
        tests: list[dict[str, Any]] = []
        summary = {
            "passed": 0,
            "flaky": 0,
            "failed": 0,
            "skipped": 0,
        }

        for nodeid, events in sorted(self._events.items()):
            call_outcomes = [
                str(event["outcome"]) for event in events if event["when"] == "call"
            ]
            final_outcome = call_outcomes[-1] if call_outcomes else None
            rerun_count = sum(event["outcome"] == "rerun" for event in events)
            categories = sorted(
                {
                    str(event["classification"]["category"])
                    for event in events
                    if "classification" in event
                }
            )
            known_flaky = next(
                (
                    event["known_flaky"]
                    for event in reversed(events)
                    if "known_flaky" in event
                ),
                None,
            )

            if final_outcome == "passed" and rerun_count > 0:
                status = "flaky"
            elif final_outcome == "passed":
                status = "passed"
            elif final_outcome == "skipped":
                status = "skipped"
            else:
                status = "failed"

            summary[status] += 1

            tests.append(
                {
                    "nodeid": nodeid,
                    "status": status,
                    "final_outcome": final_outcome,
                    "events": len(events),
                    "rerun_count": rerun_count,
                    "failure_categories": categories,
                    "known_flaky": known_flaky,
                }
            )

        return {
            "summary": summary,
            "tests": tests,
        }

    def write_json(self, path: str | Path) -> None:
        """把汇总报告写入 JSON 文件。"""
        report_path = Path(path)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(
            json.dumps(
                self.build(),
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
