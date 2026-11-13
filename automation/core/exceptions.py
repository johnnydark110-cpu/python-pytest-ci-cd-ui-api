"""自动化测试框架的异常类型。"""


class AutomationError(Exception):
    """自动化框架中所有自定义异常的基类。"""


class APIClientError(AutomationError):
    """API 客户端相关错误的基类。"""

    def __init__(
            self,
            message: str,
            *,
            method: str | None = None,
            url: str | None = None, ) -> None:
        super().__init__(message)
        self.method = method
        self.url = url


class APITransportError(APIClientError):
    """请求未能获得 HTTP 响应时抛出的异常。"""

    def __init__(self,
                 *,
                 method: str,
                 url: str,
                 cause: BaseException,)-> None:
        super().__init__(
            f"{method} {url} 请求失败: {cause}",
            method=method,
            url=url,
        )
        self.cause = cause
