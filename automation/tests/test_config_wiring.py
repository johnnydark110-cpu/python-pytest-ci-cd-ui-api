"""命令行环境选择与最终配置接线测试。"""

import os
from pathlib import Path

import pytest

from config import Settings
from core import APIClient

pytestmark = [
    pytest.mark.smoke,
    pytest.mark.regression,
]


def _optional_bool_env(name: str, default: bool) -> bool:
    """读取可选布尔环境变量；未设置时返回默认值。"""
    value = os.getenv(name)

    if value is None:
        return default

    return value.strip().lower() in {"1", "true", "yes", "on"}


EXPECTED_CONFIGS = {
    "dev": {
        "base_url": "http://127.0.0.1:8000",
        "timeout_seconds": 10.0,
        "verify_ssl": True,
        "read_only": False,
    },
    "staging": {
        "base_url": "http://127.0.0.1:8001",
        "timeout_seconds": 20.0,
        "verify_ssl": True,
        "read_only": False,
    },
    "prod": {
        "base_url": "https://prod.example.invalid",
        "timeout_seconds": 15.0,
        "verify_ssl": True,
        "read_only": True,
    },
}


def test_cli_environment_configures_fixtures(
    request: pytest.FixtureRequest,
    settings: Settings,
    base_url: str,
    api_client: APIClient,
) -> None:
    """--env 与合法环境变量覆盖应正确配置所有 fixtures。"""
    env_name = request.config.getoption("--env")
    expected = EXPECTED_CONFIGS[env_name]

    expected_environment = os.getenv(
        "AUTOMATION_ENVIRONMENT",
        env_name,
    )
    expected_base_url = os.getenv(
        "AUTOMATION_BASE_URL",
        expected["base_url"],
    ).rstrip("/")

    timeout_value = os.getenv("AUTOMATION_TIMEOUT_SECONDS")
    expected_timeout = (
        float(timeout_value)
        if timeout_value is not None
        else expected["timeout_seconds"]
    )

    expected_verify_ssl = _optional_bool_env(
        "AUTOMATION_VERIFY_SSL",
        expected["verify_ssl"],
    )
    expected_read_only = _optional_bool_env(
        "AUTOMATION_READ_ONLY",
        expected["read_only"],
    )

    assert settings.environment == expected_environment
    assert str(settings.base_url).rstrip("/") == expected_base_url
    assert settings.timeout_seconds == expected_timeout
    assert settings.verify_ssl is expected_verify_ssl
    assert settings.read_only is expected_read_only

    database_path_value = os.getenv("AUTOMATION_DATABASE_PATH")
    expected_database_path = (
        Path(database_path_value)
        if database_path_value is not None
        else Path(__file__).resolve().parents[2] / "app" / "data" / "app.db"
    )

    assert settings.database_path == expected_database_path

    assert base_url == expected_base_url
    assert api_client.base_url == expected_base_url
    assert api_client.timeout == expected_timeout
    assert api_client.verify_ssl is expected_verify_ssl
    assert api_client.read_only is expected_read_only
