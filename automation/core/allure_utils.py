"""Allure 报告附件工具。"""

from __future__ import annotations

from typing import Any

import allure
from allure_commons.types import AttachmentType

from .logger import format_log_data


def attach_redacted_json(name: str, data: Any) -> None:
    """脱敏后把数据作为 JSON 文件附加到当前 Allure 测试。"""
    allure.attach(
        body=format_log_data(data),
        name=name,
        attachment_type=AttachmentType.JSON,
    )
