"""JSON Schema 加载与响应契约校验。"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


def load_json_schema(path: str | Path) -> dict[str, Any]:
    """加载并验证 JSON Schema 文件。"""
    schema_path = Path(path)

    if not schema_path.is_file():
        raise FileNotFoundError(f"JSON Schema 不存在: {schema_path}")

    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"JSON Schema 语法错误: {schema_path}: {exc}") from exc

    if not isinstance(schema, dict):
        raise TypeError(f"JSON Schema 顶层必须是对象: {schema_path}")

    Draft202012Validator.check_schema(schema)
    return schema


def validate_json_contract(
    instance: Any,
    schema: dict[str, Any],
    *,
    label: str = "响应",
) -> None:
    """校验响应实例，聚合字段路径和错误信息。"""
    validator = Draft202012Validator(schema)
    errors = sorted(
        validator.iter_errors(instance),
        key=lambda error: tuple(str(part) for part in error.absolute_path),
    )

    if not errors:
        return

    details: list[str] = []

    for error in errors:
        location = "$"

        for part in error.absolute_path:
            if isinstance(part, int):
                location += f"[{part}]"
            else:
                location += f".{part}"

        details.append(f"{location}: {error.message}")

    raise AssertionError(f"{label}不符合 JSON Schema 契约:\n" + "\n".join(details))
