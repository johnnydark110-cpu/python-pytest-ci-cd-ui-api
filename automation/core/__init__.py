"""自动化测试框架的核心能力。"""

from .allure_utils import attach_redacted_json
from .api_client import APIClient
from .exceptions import (
    APIClientError,
    APIResponseError,
    APITransportError,
    AutomationError,
)
from .logger import configure_logging, get_logger, redact_data
from .request_context import (
    get_request_history,
    record_request_exchange,
    start_request_history,
    stop_request_history,
)
from .yaml_loader import load_yaml_test_cases

__all__ = [
    "APIClient",
    "APIClientError",
    "APIResponseError",
    "APITransportError",
    "AutomationError",
    "attach_redacted_json",
    "configure_logging",
    "get_logger",
    "get_request_history",
    "load_yaml_test_cases",
    "record_request_exchange",
    "redact_data",
    "start_request_history",
    "stop_request_history",
]
