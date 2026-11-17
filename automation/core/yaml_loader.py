"""YAML 测试数据加载与基础结构校验。"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def load_yaml_test_cases(path: str | Path) -> list[dict[str, Any]]:
    """加载 YAML 用例列表，并校验顶层结构与非空唯一 ID。"""
    yaml_path = Path(path)

    if not yaml_path.is_file():
        raise FileNotFoundError(f"测试数据文件不存在: {yaml_path}")

    raw_data = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))

    if not isinstance(raw_data, list):
        raise TypeError(f"YAML 测试数据顶层必须是列表: {yaml_path}")

    if not raw_data:
        raise ValueError(f"YAML 测试数据不能为空: {yaml_path}")

    cases: list[dict[str, Any]] = []
    seen_ids: set[str] = set()

    for index, raw_case in enumerate(raw_data, start=1):
        if not isinstance(raw_case, dict):
            raise TypeError(f"YAML 第 {index} 条测试数据必须是对象: {yaml_path}")

        case = {str(key): value for key, value in raw_case.items()}
        case_id = case.get("id")

        if not isinstance(case_id, str) or not case_id.strip():
            raise ValueError(
                f"YAML 第 {index} 条测试数据缺少非空字符串 id: {yaml_path}"
            )

        normalized_id = case_id.strip()
        if normalized_id in seen_ids:
            raise ValueError(f"YAML 测试数据存在重复 id: {normalized_id}")

        case["id"] = normalized_id
        seen_ids.add(normalized_id)
        cases.append(case)

    return cases
