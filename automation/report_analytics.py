"""聚合 flaky 结果，生成失败聚类和跨运行趋势。"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

CHANNEL_FILES = (
    "flaky-parallel.json",
    "flaky-serial.json",
    "flaky-smoke.json",
)
STATUS_RANK = {
    "passed": 0,
    "skipped": 1,
    "flaky": 2,
    "failed": 3,
}


def discover_report_files(report_dir: str | Path) -> list[Path]:
    """优先发现三个通道，其次回退到本地完整汇总。"""
    directory = Path(report_dir)

    channel_files = [
        directory / name for name in CHANNEL_FILES if (directory / name).is_file()
    ]
    if channel_files:
        return channel_files

    local_summary = directory / "flaky-summary.json"
    return [local_summary] if local_summary.is_file() else []


def load_report_file(path: str | Path) -> dict[str, Any]:
    """加载并检查单个 flaky 报告。"""
    report_path = Path(path)

    try:
        payload = json.loads(report_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"报告不是合法 JSON: {report_path}: {exc}") from exc

    if not isinstance(payload, dict):
        raise TypeError(f"报告顶层必须是对象: {report_path}")

    if not isinstance(payload.get("tests"), list):
        raise TypeError(f"报告缺少 tests 数组: {report_path}")

    return payload


def _channel_name(path: Path) -> str:
    """从 flaky-parallel.json 提取 parallel。"""
    name = path.stem
    return name.removeprefix("flaky-")


def _worse_status(current: str, candidate: str) -> str:
    """在同一测试重复出现时保留更严重状态。"""
    if STATUS_RANK.get(candidate, -1) > STATUS_RANK.get(current, -1):
        return candidate
    return current


def merge_report_files(paths: list[Path]) -> dict[str, Any]:
    """合并多个通道，并按 nodeid 去重。"""
    merged_tests: dict[str, dict[str, Any]] = {}

    for path in paths:
        payload = load_report_file(path)
        channel = _channel_name(path)

        for raw_test in payload["tests"]:
            if not isinstance(raw_test, dict):
                continue

            nodeid = str(raw_test.get("nodeid", "")).strip()
            if not nodeid:
                continue

            categories = sorted(
                {
                    str(category)
                    for category in raw_test.get(
                        "failure_categories",
                        [],
                    )
                    if category
                }
            )
            current = merged_tests.get(nodeid)

            if current is None:
                merged_tests[nodeid] = {
                    "nodeid": nodeid,
                    "status": str(raw_test.get("status", "unknown")),
                    "final_outcome": raw_test.get("final_outcome"),
                    "events": int(raw_test.get("events", 0)),
                    "rerun_count": int(raw_test.get("rerun_count", 0)),
                    "failure_categories": categories,
                    "known_flaky": raw_test.get("known_flaky"),
                    "channels": [channel],
                }
                continue

            current["status"] = _worse_status(
                str(current["status"]),
                str(raw_test.get("status", "unknown")),
            )
            current["events"] = max(
                int(current["events"]),
                int(raw_test.get("events", 0)),
            )
            current["rerun_count"] = max(
                int(current["rerun_count"]),
                int(raw_test.get("rerun_count", 0)),
            )
            current["failure_categories"] = sorted(
                set(current["failure_categories"]) | set(categories)
            )
            current["known_flaky"] = current["known_flaky"] or raw_test.get(
                "known_flaky"
            )
            current["channels"] = sorted(set(current["channels"]) | {channel})

    tests = sorted(
        merged_tests.values(),
        key=lambda test: str(test["nodeid"]),
    )
    summary = {
        "passed": 0,
        "flaky": 0,
        "failed": 0,
        "skipped": 0,
    }

    for test in tests:
        status = str(test["status"])
        if status in summary:
            summary[status] += 1

    return {
        "summary": summary,
        "tests": tests,
    }


def build_failure_clusters(
    tests: list[dict[str, Any]],
) -> dict[str, Any]:
    """按失败类别、模块和 known_flaky issue 聚类。"""
    by_category: Counter[str] = Counter()
    by_module: Counter[str] = Counter()
    known_issues: Counter[str] = Counter()
    items: list[dict[str, Any]] = []

    for test in tests:
        status = str(test.get("status", ""))
        if status not in {"failed", "flaky"}:
            continue

        nodeid = str(test.get("nodeid", ""))
        module = nodeid.split("::", 1)[0]
        categories = test.get("failure_categories") or ["unclassified"]

        by_module[module] += 1

        known_flaky = test.get("known_flaky")
        issue = (
            str(known_flaky.get("issue"))
            if isinstance(known_flaky, dict) and known_flaky.get("issue")
            else None
        )
        if issue:
            known_issues[issue] += 1

        for category in categories:
            category_name = str(category)
            by_category[category_name] += 1
            items.append(
                {
                    "category": category_name,
                    "module": module,
                    "nodeid": nodeid,
                    "status": status,
                    "rerun_count": int(test.get("rerun_count", 0)),
                    "issue": issue,
                }
            )

    return {
        "by_category": dict(sorted(by_category.items())),
        "by_module": dict(sorted(by_module.items())),
        "known_flaky_issues": dict(sorted(known_issues.items())),
        "items": sorted(
            items,
            key=lambda item: (
                str(item["category"]),
                str(item["module"]),
                str(item["nodeid"]),
            ),
        ),
    }


def load_history(path: str | Path) -> dict[str, Any]:
    """加载历史；文件不存在时返回空历史。"""
    history_path = Path(path)

    if not history_path.is_file():
        return {
            "schema_version": 1,
            "runs": [],
        }

    payload = json.loads(history_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or not isinstance(
        payload.get("runs"),
        list,
    ):
        raise TypeError(f"历史文件格式错误: {history_path}")
    return payload


def update_history(
    history: dict[str, Any],
    current: dict[str, Any],
    *,
    max_runs: int,
) -> dict[str, Any]:
    """追加当前运行，替换相同 run_id，并限制历史长度。"""
    if max_runs < 1:
        raise ValueError("max_runs 必须大于等于 1")

    run_id = str(current["metadata"]["run_id"])
    runs = [run for run in history.get("runs", []) if str(run.get("run_id")) != run_id]
    runs.append(
        {
            "run_id": run_id,
            "metadata": current["metadata"],
            "summary": current["summary"],
            "clusters": {
                "by_category": current["clusters"]["by_category"],
                "by_module": current["clusters"]["by_module"],
                "known_flaky_issues": current["clusters"]["known_flaky_issues"],
            },
        }
    )

    return {
        "schema_version": 1,
        "runs": runs[-max_runs:],
    }


def build_dashboard(
    current: dict[str, Any],
    history: dict[str, Any],
) -> dict[str, Any]:
    """生成当前结果、趋势和聚类汇总。"""
    trend = [
        {
            "run_id": run["run_id"],
            "timestamp": run["metadata"]["timestamp"],
            "commit": run["metadata"]["commit"],
            "summary": run["summary"],
        }
        for run in history["runs"]
    ]

    return {
        "schema_version": 1,
        "current": current,
        "trend": trend,
    }


def render_markdown(
    current: dict[str, Any],
    history: dict[str, Any],
) -> str:
    """生成 GitHub Actions Job Summary。"""
    metadata = current["metadata"]
    summary = current["summary"]
    clusters = current["clusters"]

    lines = [
        "## 自动化失败分析与趋势",
        "",
        f"- Run ID：`{metadata['run_id']}`",
        f"- Commit：`{str(metadata['commit'])[:12]}`",
        f"- Branch：`{metadata['branch']}`",
        f"- 时间：`{metadata['timestamp']}`",
        "",
        "### 当前结果",
        "",
        "| 状态 | 数量 |",
        "|---|---:|",
        f"| Passed | {summary['passed']} |",
        f"| Flaky | {summary['flaky']} |",
        f"| Failed | {summary['failed']} |",
        f"| Skipped | {summary['skipped']} |",
        "",
        "### 失败聚类",
        "",
    ]

    if clusters["by_category"]:
        lines.extend(
            [
                "| 类别 | 数量 |",
                "|---|---:|",
            ]
        )
        lines.extend(
            f"| `{name}` | {count} |" for name, count in clusters["by_category"].items()
        )
    else:
        lines.append("当前运行没有失败或 flaky 聚类。")

    lines.extend(
        [
            "",
            "### 最近趋势",
            "",
            "| Run ID | Commit | Passed | Flaky | Failed |",
            "|---|---|---:|---:|---:|",
        ]
    )

    for run in history["runs"][-10:]:
        run_summary = run["summary"]
        lines.append(
            f"| `{run['run_id']}` "
            f"| `{str(run['metadata']['commit'])[:8]}` "
            f"| {run_summary['passed']} "
            f"| {run_summary['flaky']} "
            f"| {run_summary['failed']} |"
        )

    return "\n".join(lines) + "\n"


def _write_json(path: str | Path, payload: dict[str, Any]) -> None:
    """写入格式化 JSON。"""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    """命令行入口。"""
    parser = argparse.ArgumentParser(description="聚合 flaky 结果并生成趋势报告")
    parser.add_argument(
        "--report-dir",
        default="reports",
        help="flaky 报告目录",
    )
    parser.add_argument(
        "--report-file",
        action="append",
        default=[],
        help="显式指定报告文件，可重复使用",
    )
    parser.add_argument(
        "--history",
        default="reports/analytics/history.json",
    )
    parser.add_argument(
        "--output",
        default="reports/analytics/dashboard.json",
    )
    parser.add_argument(
        "--summary-md",
        default="reports/analytics/summary.md",
    )
    parser.add_argument(
        "--max-history",
        type=int,
        default=30,
    )
    parser.add_argument("--run-id", default="local")
    parser.add_argument("--commit", default="local")
    parser.add_argument("--branch", default="local")
    args = parser.parse_args()

    report_files = (
        [Path(path) for path in args.report_file]
        if args.report_file
        else discover_report_files(args.report_dir)
    )
    report_files = [path for path in report_files if path.is_file()]

    if not report_files:
        print("未找到可分析的 flaky 报告。")
        return 2

    try:
        merged = merge_report_files(report_files)
        clusters = build_failure_clusters(merged["tests"])
        current = {
            "metadata": {
                "run_id": args.run_id,
                "commit": args.commit,
                "branch": args.branch,
                "timestamp": datetime.now(UTC).isoformat(timespec="seconds"),
                "source_files": [str(path) for path in report_files],
            },
            "summary": merged["summary"],
            "clusters": clusters,
            "tests": merged["tests"],
        }
        history = load_history(args.history)
        history = update_history(
            history,
            current,
            max_runs=args.max_history,
        )
        dashboard = build_dashboard(current, history)

        _write_json(args.output, dashboard)
        _write_json(args.history, history)

        summary_path = Path(args.summary_md)
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        summary_path.write_text(
            render_markdown(current, history),
            encoding="utf-8",
        )
    except (OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
        print(f"分析失败: {exc}")
        return 2

    print(
        "analytics: "
        f"passed={merged['summary']['passed']}, "
        f"flaky={merged['summary']['flaky']}, "
        f"failed={merged['summary']['failed']}, "
        f"skipped={merged['summary']['skipped']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
