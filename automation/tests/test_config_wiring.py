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
    """所选环境应正确配置 Settings、URL 和 API 客户端。"""
    env_name = request.config.getoption("--env")
    expected = EXPECTED_CONFIGS[env_name]

    assert settings.environment == env_name
    assert str(settings.base_url).rstrip("/") == expected["base_url"]
    assert settings.timeout_seconds == expected["timeout_seconds"]
    assert settings.verify_ssl is expected["verify_ssl"]

    assert base_url == expected["base_url"]
    assert api_client.base_url == expected["base_url"]
    assert api_client.timeout == expected["timeout_seconds"]
    assert api_client.verify_ssl is expected["verify_ssl"]
