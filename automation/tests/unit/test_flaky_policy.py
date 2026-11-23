"""失败分类、known_flaky 和重试汇总测试。"""

from datetime import date

import pytest

from core import (
    APITransportError,
    FlakyAttemptLedger,
    ReadOnlyViolationError,
    classify_failure,
    validate_known_flaky_metadata,
)

pytestmark = pytest.mark.regression


@pytest.mark.parametrize(
    ("exception", "expected_category"),
    [
        (
            APITransportError(
                method="GET",
                url="https://safe.local/api/orders",
                cause=ConnectionError("refused"),
            ),
            "environment",
        ),
        (
            AssertionError("amount mismatch"),
            "product_assertion",
        ),
        (
            ReadOnlyViolationError(
                method="POST",
                url="https://safe.local/api/orders",
            ),
            "configuration",
        ),
        (
            NameError("name 'helper' is not defined"),
            "framework_or_test",
        ),
    ],
)
def test_failure_classification(
    exception: BaseException,
    expected_category: str,
) -> None:
    """典型失败应进入稳定分类。"""
    classification = classify_failure(exception)

    assert classification.category == expected_category
    assert classification.exception_type
    assert classification.reason
    assert classification.triage


def test_known_flaky_metadata_accepts_valid_record() -> None:
    """完整的未过期登记应通过校验。"""
    policy = validate_known_flaky_metadata(
        issue="ISSUE-123",
        owner="qa-team",
        expires="2026-12-31",
        reason="等待异步索引修复",
        today=date(2026, 11, 23),
    )

    assert policy.issue == "ISSUE-123"
    assert policy.owner == "qa-team"
    assert policy.expires == "2026-12-31"


@pytest.mark.parametrize(
    "metadata",
    [
        {
            "issue": "ISSUE-OLD",
            "owner": "qa-team",
            "expires": "2026-11-22",
            "reason": "已过期",
        },
        {
            "issue": "",
            "owner": "qa-team",
            "expires": "2026-12-31",
            "reason": "缺少 issue",
        },
    ],
)
def test_known_flaky_metadata_rejects_invalid_record(
    metadata: dict[str, str],
) -> None:
    """过期或缺少 issue 的登记必须被拒绝。"""
    with pytest.raises(ValueError):
        validate_known_flaky_metadata(
            **metadata,
            today=date(2026, 11, 23),
        )


def test_ledger_marks_retry_pass_as_flaky() -> None:
    """先失败重试后通过应汇总为 flaky。"""
    ledger = FlakyAttemptLedger()

    ledger.record(
        nodeid="tests/api/test_example.py::test_example",
        outcome="rerun",
        when="call",
        classification={"category": "environment"},
        known_flaky={
            "issue": "ISSUE-123",
            "owner": "qa-team",
            "expires": "2026-12-31",
            "reason": "环境抖动",
        },
    )
    ledger.record(
        nodeid="tests/api/test_example.py::test_example",
        outcome="passed",
        when="call",
    )

    report = ledger.build()
    test_result = report["tests"][0]

    assert report["summary"]["flaky"] == 1
    assert test_result["status"] == "flaky"
    assert test_result["rerun_count"] == 1
    assert test_result["failure_categories"] == ["environment"]
    assert test_result["known_flaky"]["issue"] == "ISSUE-123"


def test_ledger_marks_final_failure() -> None:
    """最终仍然失败时不得归类为 flaky。"""
    ledger = FlakyAttemptLedger()

    ledger.record(
        nodeid="tests/api/test_example.py::test_failure",
        outcome="failed",
        when="call",
        classification={"category": "product_assertion"},
    )

    report = ledger.build()
    test_result = report["tests"][0]

    assert report["summary"]["failed"] == 1
    assert test_result["status"] == "failed"
    assert test_result["failure_categories"] == ["product_assertion"]
