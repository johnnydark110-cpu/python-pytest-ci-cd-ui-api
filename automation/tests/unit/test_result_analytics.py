"""失败聚类和趋势分析测试。"""

from __future__ import annotations

import json
from pathlib import Path

from report_analytics import (
    build_failure_clusters,
    discover_report_files,
    merge_report_files,
    render_markdown,
    update_history,
)


def _write_report(
    path: Path,
    tests: list[dict],
) -> None:
    """写入最小 flaky 报告。"""
    path.write_text(
        json.dumps(
            {
                "summary": {},
                "tests": tests,
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def test_discover_report_files_prefers_channels(
    tmp_path: Path,
) -> None:
    """存在通道报告时不应读取本地 summary 重复计数。"""
    for name in (
        "flaky-parallel.json",
        "flaky-serial.json",
        "flaky-smoke.json",
        "flaky-summary.json",
    ):
        _write_report(tmp_path / name, [])

    files = discover_report_files(tmp_path)

    assert [path.name for path in files] == [
        "flaky-parallel.json",
        "flaky-serial.json",
        "flaky-smoke.json",
    ]


def test_merge_report_files_deduplicates_and_unions_categories(
    tmp_path: Path,
) -> None:
    """重复 nodeid 应合并为更严重状态。"""
    parallel = tmp_path / "flaky-parallel.json"
    serial = tmp_path / "flaky-serial.json"

    _write_report(
        parallel,
        [
            {
                "nodeid": "tests/test_example.py::test_case",
                "status": "flaky",
                "final_outcome": "passed",
                "events": 2,
                "rerun_count": 1,
                "failure_categories": ["environment"],
                "known_flaky": None,
            }
        ],
    )
    _write_report(
        serial,
        [
            {
                "nodeid": "tests/test_example.py::test_case",
                "status": "failed",
                "final_outcome": "failed",
                "events": 1,
                "rerun_count": 0,
                "failure_categories": ["product_assertion"],
                "known_flaky": {"issue": "ISSUE-1"},
            }
        ],
    )

    merged = merge_report_files([parallel, serial])
    test = merged["tests"][0]

    assert merged["summary"]["failed"] == 1
    assert test["status"] == "failed"
    assert test["failure_categories"] == [
        "environment",
        "product_assertion",
    ]
    assert test["channels"] == ["parallel", "serial"]


def test_build_failure_clusters_groups_category_module_and_issue() -> None:
    """失败应按类别、模块和 issue 聚类。"""
    tests = [
        {
            "nodeid": "tests/api/test_order.py::test_order",
            "status": "failed",
            "failure_categories": ["product_assertion"],
            "rerun_count": 0,
            "known_flaky": {
                "issue": "ISSUE-1",
            },
        },
        {
            "nodeid": "tests/ui/test_login.py::test_login",
            "status": "flaky",
            "failure_categories": ["environment"],
            "rerun_count": 1,
            "known_flaky": None,
        },
    ]

    clusters = build_failure_clusters(tests)

    assert clusters["by_category"] == {
        "environment": 1,
        "product_assertion": 1,
    }
    assert clusters["by_module"] == {
        "tests/api/test_order.py": 1,
        "tests/ui/test_login.py": 1,
    }
    assert clusters["known_flaky_issues"] == {
        "ISSUE-1": 1,
    }


def test_update_history_replaces_run_and_caps_length() -> None:
    """相同 run_id 应替换，历史数量应受上限约束。"""
    current = {
        "metadata": {
            "run_id": "run-2",
            "timestamp": "2026-11-23T10:00:00+00:00",
            "commit": "abcdef123456",
            "branch": "master",
        },
        "summary": {
            "passed": 90,
            "flaky": 2,
            "failed": 1,
            "skipped": 0,
        },
        "clusters": {
            "by_category": {
                "environment": 1,
            },
            "by_module": {
                "tests/api/test_example.py": 1,
            },
            "known_flaky_issues": {},
        },
    }
    history = {
        "schema_version": 1,
        "runs": [
            {"run_id": "run-1"},
            {"run_id": "run-2"},
        ],
    }

    updated = update_history(
        history,
        current,
        max_runs=1,
    )

    assert len(updated["runs"]) == 1
    assert updated["runs"][0]["run_id"] == "run-2"


def test_render_markdown_contains_summary_clusters_and_trend() -> None:
    """Actions 摘要应包含状态、聚类和最近趋势。"""
    current = {
        "metadata": {
            "run_id": "run-1",
            "timestamp": "2026-11-23T10:00:00+00:00",
            "commit": "abcdef123456",
            "branch": "master",
        },
        "summary": {
            "passed": 10,
            "flaky": 1,
            "failed": 2,
            "skipped": 0,
        },
        "clusters": {
            "by_category": {
                "product_assertion": 2,
            },
            "by_module": {
                "tests/test_example.py": 2,
            },
            "known_flaky_issues": {},
        },
    }
    history = {
        "runs": [
            {
                **current,
                "run_id": "run-1",
            }
        ]
    }

    markdown = render_markdown(current, history)

    assert "自动化失败分析与趋势" in markdown
    assert "`product_assertion` | 2" in markdown
    assert "Passed | 10" in markdown
    assert "run-1" in markdown
