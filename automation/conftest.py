"""pytest 的共享 fixture 入口。"""

import logging
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
from playwright.sync_api import BrowserContext, Page

from config import (
    ExecutionProfile,
    Settings,
    resolve_execution_profile,
)
from core import (
    APIClient,
    BrowserManager,
    DBClient,
    attach_redacted_json,
    attach_screenshot,
    configure_logging,
    get_logger,
    get_request_history,
    get_trace_context,
    start_request_history,
    start_trace_context,
    stop_request_history,
    stop_trace_context,
)
from pages import BasePage
from services import AuthService, OrderService, TokenManager
from utils import OrderData, TestDataFactory

CONFIG_DIR = Path(__file__).resolve().parent / "config"
logger = get_logger(__name__)


def pytest_addoption(parser) -> None:
    parser.addoption(
        "--env",
        action="store",
        default="dev",
        choices=("dev", "staging", "prod"),
        help="选择自动化测试环境配置，默认 dev",
    )
    parser.addoption(
        "--suite",
        action="store",
        default=None,
        choices=("full", "regression", "smoke"),
        help="选择执行档位；未指定时使用环境默认档位",
    )


def _resolve_execution_profile(
    config: pytest.Config,
) -> ExecutionProfile:
    """从命令行解析当前环境和执行档位。"""
    return resolve_execution_profile(
        environment=config.getoption("--env"),
        requested_suite=config.getoption("--suite"),
    )


def pytest_configure(config: pytest.Config) -> None:
    """在收集测试前拒绝不安全的环境与档位组合。"""
    try:
        _resolve_execution_profile(config)
    except ValueError as exc:
        raise pytest.UsageError(str(exc)) from exc


def pytest_report_header(config: pytest.Config) -> list[str]:
    """在 pytest 头部显示最终执行策略。"""
    profile = _resolve_execution_profile(config)

    return [
        f"automation environment: {profile.environment}",
        f"automation suite: {profile.suite}",
    ]


def pytest_collection_modifyitems(
    config: pytest.Config,
    items: list[pytest.Item],
) -> None:
    """根据执行档位取消选择不适用于当前环境的测试。"""
    profile = _resolve_execution_profile(config)

    if profile.marker is None:
        return

    selected: list[pytest.Item] = []
    deselected: list[pytest.Item] = []

    for item in items:
        if item.get_closest_marker(profile.marker) is None:
            deselected.append(item)
        else:
            selected.append(item)

    if deselected:
        config.hook.pytest_deselected(items=deselected)

    items[:] = selected


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
    browser_manager: BrowserManager,
    base_url: str,
    settings: Settings,
    test_trace: None,
) -> Iterator[BrowserContext]:
    """每条测试使用独立BrowserContext，并注入染色请求头。"""
    context = browser_manager.new_context(
        base_url=base_url,
        ignore_https_errors=not settings.verify_ssl,
    )

    trace = get_trace_context()
    if trace is not None:
        context.set_extra_http_headers(trace.headers)

    try:
        yield context
    finally:
        context.close()


@pytest.fixture(scope="function")
def page(browser_context: BrowserContext) -> Iterator[Page]:
    """每条测试使用独立 Page。"""
    page = browser_context.new_page()
    yield page
    page.close()


@pytest.fixture(autouse=True)
def test_trace(settings: Settings) -> Iterator[None]:
    """每条测试开始时生成独立 trace_id。"""
    token = start_trace_context(
        traffic_tag=settings.traffic_tag,
    )

    try:
        yield
    finally:
        stop_trace_context(token)


@pytest.fixture(autouse=True)
def request_history_capture(test_trace: None) -> Iterator[None]:
    """每条测试开始前创建独立的请求历史，结束后清理。"""
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
    trace = get_trace_context()

    attach_redacted_json(
        name=f"失败上下文（{report.when}）",
        data={
            "test": item.nodeid,
            "phase": report.when,
            "trace_id": trace.trace_id if trace is not None else None,
            "traffic_tag": trace.traffic_tag if trace is not None else None,
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
def db_client(settings: Settings) -> DBClient:
    """提供 SQLite 测试数据校验与清理客户端。"""
    return DBClient(settings.database_path)


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
        read_only=settings.read_only,
    ) as client:
        yield client


@pytest.fixture(scope="session")
def auth_service(api_client: APIClient) -> AuthService:
    """共享无状态的鉴权服务。"""
    return AuthService(api_client)


@pytest.fixture(scope="session")
def data_factory() -> TestDataFactory:
    """整个 worker 会话共享一个动态数据生成器。"""
    return TestDataFactory()


@pytest.fixture(scope="function")
def auth_user(
    data_factory: TestDataFactory,
    db_client: DBClient,
) -> Iterator[dict[str, str]]:
    """生成唯一用户，并在测试结束后删除用户及关联数据。"""
    user = data_factory.user()
    user_dict = {
        "username": user.username,
        "password": user.password,
    }

    try:
        yield user_dict
    finally:
        db_client.delete_user_by_username(user.username)
        assert not db_client.user_exists(user.username), (
            f"测试用户清理失败: {user.username}"
        )


@pytest.fixture(scope="function")
def token(token_manager: TokenManager) -> str:
    """提供当前测试的有效 token。"""
    return token_manager.get_valid_token()


@pytest.fixture(scope="function")
def token_manager(
    auth_service: AuthService,
    auth_user: dict[str, str],
    api_client: APIClient,
) -> TokenManager:
    """注册当前用户，并提供测试级 token 管理器。"""
    register_response = auth_service.register(
        username=auth_user["username"],
        password=auth_user["password"],
    )
    assert register_response.status_code == 201, register_response.text

    def validate_token(token: str) -> bool:
        orders = OrderService(api_client, token)
        response = orders.list_orders(
            page=1,
            page_size=1,
        )
        return response.status_code == 200

    return TokenManager(
        auth_service,
        username=auth_user["username"],
        password=auth_user["password"],
        validator=validate_token,
    )


@pytest.fixture(scope="function")
def order_service(api_client: APIClient, token: str) -> OrderService:
    return OrderService(api_client, token)


@pytest.fixture(scope="function")
def order_data(
    data_factory: TestDataFactory,
) -> OrderData:
    """生成当前测试使用的订单输入数据。"""
    return data_factory.order()


@pytest.fixture(scope="function")
def created_order(
    order_data: OrderData,
    order_service: OrderService,
) -> Iterator[tuple[OrderData, dict[str, Any]]]:
    """通过 API 创建订单，并在测试结束后删除和确认清理。"""
    response = order_service.create_order(
        title=order_data.title,
        amount=order_data.amount,
        status=order_data.status,
    )
    assert response.status_code == 201, response.text

    created = response.json()
    order_id = created["id"]

    try:
        yield order_data, created
    finally:
        delete_response = order_service.delete_order(order_id)
        assert delete_response.status_code in {204, 404}, (
            f"订单清理失败: {delete_response.status_code} {delete_response.text}"
        )

        missing_response = order_service.get_order(order_id)
        assert missing_response.status_code == 404, "订单删除后仍可查询，数据清理未完成"
