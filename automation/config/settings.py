"""类型安全的 YAML 环境配置。"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Literal

import yaml
from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """测试环境配置模型。"""

    model_config = SettingsConfigDict(
        env_prefix="AUTOMATION_",
        case_sensitive=False,
        extra="forbid",
    )

    environment: Literal["dev", "staging"]
    base_url: AnyHttpUrl
    timeout_seconds: float = Field(
        default=10.0,
        gt=0,
        le=120,
    )
    verify_ssl: bool = True

    @classmethod
    def from_yaml(cls, path: str | Path) -> Settings:
        """从 YAML 文件加载配置，并应用环境变量覆盖。"""
        yaml_path = Path(path)

        if not yaml_path.is_file():
            raise FileNotFoundError(f"配置文件不存在: {yaml_path}")

        raw_data = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))

        if raw_data is None:
            raw_data = {}

        if not isinstance(raw_data, dict):
            raise TypeError(f"配置文件顶层必须是 YAML 对象: {yaml_path}")

        data = {str(key): value for key, value in raw_data.items()}

        for field_name in cls.model_fields:
            env_name = f"AUTOMATION_{field_name.upper()}"
            env_value = os.getenv(env_name)
            if env_value is not None:
                data[field_name] = env_value

        return cls(**data)
