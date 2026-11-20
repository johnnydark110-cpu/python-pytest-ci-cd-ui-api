"""pytest 的共享 fixture 入口。"""

import logging
from collections.abc import Iterator
from pathlib import Path
from uuid import uuid4

import pytest
from playwright.sync_api import BrowserContext, Page

from config import Settings
from core import (
    APIClient,
    BrowserManager,
    attach_redacted_json,
    attach_screenshot,
    configure_logging,
    get_logger,
    get_request_history,
    start_request_history,
    stop_request_history,
)
from pages import BasePage
from services import AuthService, OrderService

CONFIG_DIR = Path(__file__).resolve().parent / "config"
logger = get_logger(__name__)


def pytest_addoption(parser) -> None:
    parser.addoption(
        "--env",
        action="store",
        default="dev",
        choices=("dev", "staging"),
        help="选择自动化测试环境配置，默认 dev",
    )


@pytest.fixture(scope="session")
def browser_manager() -> Iterator[BrowserManager]:
    """整个测试会话共享一个 Chromium 浏览器进程。"""
    with BrowserManager(
        headless=True,
        slow_mo=0,
    ) as manager:
        yield manager


@pytest.fixture(scope="function")
def browser_context(
    browser_manager: BrowserManager, base_url: str, settings: Settings
) -> Iterator[BrowserContext]:
    """每条测试使用独立BrowserContext"""
    context = browser_manager.new_context(
        base_url=base_url,
        ignore_https_errors=not settings.verify_ssl,
    )
    yield context
    context.close()


@pytest.fixture(scope="function")
def page(browser_context: BrowserContext) -> Iterator[Page]:
    """每条测试使用独立 Page。"""
    page = browser_context.new_page()
    yield page
    page.close()


@pytest.fixture(autouse=True)
def request_history_capture() -> Iterator[None]:
    """每条测试开始前创建请求历史，结束后清理。"""
    start_request_history()
    yield
    stop_request_history()


def _attach_failure_screenshot(item, report) -> None:
    """测试失败时尝试截取当前页面，并隔离截图自身异常。"""
    page = item.funcargs.get("page")

    if not isinstance(page, Page):
        return

    try:
        if page.is_closed():
            return

        screenshot_path = BasePage(page).screenshot(
            f"failure-{report.when}-{item.name}",
        )
        attach_screenshot(
            screenshot_path,
            name=f"失败截图（{report.when}）",
        )
    except Exception as exc:
        logger.exception(
            "自动截图失败: %s",
            item.nodeid,
        )
        attach_redacted_json(
            name="自动截图失败",
            data={
                "test": item.nodeid,
                "phase": report.when,
                "error_type": type(exc).__name__,
                "error": str(exc),
            },
        )


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """失败时附加 UI 截图和本次测试的 API 请求响应上下文。"""
    outcome = yield
    report = outcome.get_result()

    if not report.failed:
        return

    _attach_failure_screenshot(item, report)

    history = get_request_history()
    if not history:
        return

    attach_redacted_json(
        name=f"失败上下文（{report.when}）",
        data={
            "test": item.nodeid,
            "phase": report.when,
            "request_count": len(history),
            "exchanges": history,
        },
    )


@pytest.fixture(scope="session")
def settings(request: pytest.FixtureRequest) -> Settings:
    """根据 --env 加载对应的 YAML 配置。"""
    env_name = request.config.getoption("--env")
    config_path = CONFIG_DIR / f"{env_name}.yaml"
    return Settings.from_yaml(config_path)


@pytest.fixture(scope="session")
def session_context() -> Iterator[dict[str, str]]:
    """整个测试会话只创建一次的共享上下文。"""
    print("\n[fixture setup] session_context")
    yield {"scope": "session", "suite_id": "local-suite"}
    print("[fixture teardown] session_context")


@pytest.fixture(scope="function")
def function_context(
    session_context: dict[str, str],
) -> Iterator[dict[str, str]]:
    """每条测试函数独立创建并销毁的上下文。"""
    print("[fixture setup] function_context")
    yield {
        "scope": "function",
        "suite_id": session_context["suite_id"],
    }
    print("[fixture teardown] function_context")


@pytest.fixture(scope="session")
def base_url(settings: Settings) -> str:
    """提供当前测试环境的基础url"""
    return str(settings.base_url).rstrip("/")


@pytest.fixture(scope="session")
def api_client(base_url: str, settings: Settings) -> Iterator[APIClient]:
    """根据当前环境配置创建共享 HTTP 客户端。"""
    configure_logging(logging.INFO)

    with APIClient(
        base_url=base_url,
        timeout=settings.timeout_seconds,
        verify_ssl=settings.verify_ssl,
    ) as client:
        yield client


@pytest.fixture(scope="session")
def auth_service(api_client: APIClient) -> AuthService:
    """共享无状态的鉴权服务。"""
    return AuthService(api_client)


@pytest.fixture(scope="function")
def auth_user() -> dict[str, str]:
    suffix = uuid4().hex[:10]
    return {
        "username": f"api_{suffix}",
        "password": "secret123",
    }


@pytest.fixture(scope="function")
def token(
    auth_service: AuthService,
    auth_user: dict[str, str],
) -> str:
    """为当前测试创建独立用户并登录取得 token。"""

    register_response = auth_service.register(
        username=auth_user["username"],
        password=auth_user["password"],
    )
    assert register_response.status_code == 201, register_response.text

    return auth_service.get_token(
        username=auth_user["username"],
        password=auth_user["password"],
    )


@pytest.fixture(scope="function")
def order_service(api_client: APIClient, token: str) -> OrderService:
    return OrderService(api_client, token)
