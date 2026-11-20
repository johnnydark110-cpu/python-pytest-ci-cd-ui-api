"""命令行环境选择与最终配置接线测试。"""

import os

import pytest

from config import Settings
from core import APIClient

pytestmark = [
    pytest.mark.smoke,
    pytest.mark.regression,
]

EXPECTED_CONFIGS = {
    "dev": {
        "base_url": "http://127.0.0.1:8000",
        "timeout_seconds": 10.0,
        "verify_ssl": True,
    },
    "staging": {
        "base_url": "http://127.0.0.1:8001",
        "timeout_seconds": 20.0,
        "verify_ssl": True,
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

    verify_ssl_value = os.getenv("AUTOMATION_VERIFY_SSL")
    expected_verify_ssl = (
        expected["verify_ssl"]
        if verify_ssl_value is None
        else verify_ssl_value.strip().lower() in {"1", "true", "yes", "on"}
    )

    assert settings.environment == expected_environment
    assert str(settings.base_url).rstrip("/") == expected_base_url
    assert settings.timeout_seconds == expected_timeout
    assert settings.verify_ssl is expected_verify_ssl

    assert base_url == expected_base_url
    assert api_client.base_url == expected_base_url
    assert api_client.timeout == expected_timeout
    assert api_client.verify_ssl is expected_verify_ssl
