"""Allure 报告附件工具。"""

from __future__ import annotations

from pathlib import Path
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


def attach_screenshot(
    path: str | Path,
    *,
    name: str = "失败截图",
) -> None:
    """把 PNG 截图附加到当前 Allure 测试。"""
    screenshot_path = Path(path)

    if not screenshot_path.is_file():
        raise FileNotFoundError(f"截图文件不存在: {screenshot_path}")

    allure.attach.file(
        str(screenshot_path),
        name=name,
        attachment_type=AttachmentType.PNG,
    )
