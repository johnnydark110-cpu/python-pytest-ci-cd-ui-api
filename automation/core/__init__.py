"""自动化测试框架的核心能力。"""

from .allure_utils import attach_redacted_json, attach_screenshot
from .api_client import APIClient
from .db_client import DBClient
from .exceptions import (
    APIClientError,
    APIResponseError,
    APITransportError,
    AutomationError,
    CircuitOpenError,
    ReadOnlyViolationError,
)
from .logger import configure_logging, get_logger, redact_data
from .request_context import (
    get_request_history,
    record_request_exchange,
    start_request_history,
    stop_request_history,
)
from .request_guard import (
    CircuitBreaker,
    RequestRateLimiter,
)
from .schema_validator import (
    load_json_schema,
    validate_json_contract,
)
from .trace_context import (
    TRACE_ID_HEADER,
    TRAFFIC_TAG_HEADER,
    TraceContext,
    get_trace_context,
    get_trace_id,
    start_trace_context,
    stop_trace_context,
)
from .web_driver import BrowserManager
from .yaml_loader import load_yaml_test_cases

__all__ = [
    "TRACE_ID_HEADER",
    "TRAFFIC_TAG_HEADER",
    "APIClient",
    "APIClientError",
    "APIResponseError",
    "APITransportError",
    "AutomationError",
    "BrowserManager",
    "CircuitBreaker",
    "CircuitOpenError",
    "DBClient",
    "ReadOnlyViolationError",
    "RequestRateLimiter",
    "TraceContext",
    "attach_redacted_json",
    "attach_screenshot",
    "configure_logging",
    "get_logger",
    "get_request_history",
    "get_trace_context",
    "get_trace_id",
    "load_json_schema",
    "load_yaml_test_cases",
    "record_request_exchange",
    "redact_data",
    "start_request_history",
    "start_trace_context",
    "stop_request_history",
    "stop_trace_context",
    "validate_json_contract",
]
