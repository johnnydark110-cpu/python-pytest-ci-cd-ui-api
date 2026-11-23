"""自动化测试框架的异常类型。"""

from __future__ import annotations

from typing import Any

"""
继承 `Exception`（**不要继承 BaseException！** BaseException 包含 KeyboardInterrupt、系统退出，业务异常不要抓）
"""


class AutomationError(Exception):
    """自动化框架中所有自定义异常的基类。"""


class APIClientError(AutomationError):
    """API 客户端相关错误的基类。"""

    def __init__(
        self,
        message: str,
        *,
        method: str | None = None,
        url: str | None = None,
    ) -> None:
        super().__init__(message)
        self.method = method
        self.url = url


class ReadOnlyViolationError(APIClientError):
    """只读模式阻止了可能修改数据的 HTTP 请求。"""

    def __init__(
        self,
        *,
        method: str,
        url: str,
    ) -> None:
        super().__init__(
            f"只读模式禁止写请求: {method} {url}",
            method=method,
            url=url,
        )


class APITransportError(APIClientError):
    """请求未能获得 HTTP 响应时抛出的异常。"""

    def __init__(
        self,
        *,
        method: str,
        url: str,
        cause: BaseException,
    ) -> None:
        super().__init__(
            f"{method} {url} 请求失败: {cause}",
            method=method,
            url=url,
        )
        self.cause = cause


class APIResponseError(APIClientError):
    """业务要求成功响应，但服务端返回非预期状态时抛出的异常。"""

    def __init__(
        self,
        message: str,
        *,
        status_code: int,
        body: Any,
        method: str | None = None,
        url: str | None = None,
    ) -> None:
        super().__init__(message, method=method, url=url)
        self.status_code = status_code
        self.body = body
