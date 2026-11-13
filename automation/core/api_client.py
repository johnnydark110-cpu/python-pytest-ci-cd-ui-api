import logging
from collections.abc import Mapping
from time import perf_counter
from types import TracebackType
from typing import Any

import httpx

"""统一封装 HTTP 请求的基础 API 客户端。"""

logger = logging.getLogger(__name__)
DEFAULT_BASE_URL = "http://127.0.0.1:8000"
DEFAULT_TIMEOUT_SECONDS = 10.0


class APIClient:
    """为测试框架提供统一配置和请求日志的 HTTP 客户端。"""

    def __init__(self,
                 base_url: str = DEFAULT_BASE_URL,
                 timeout: float | httpx.Timeout = DEFAULT_TIMEOUT_SECONDS,
                 default_headers: Mapping[str, str] | None = None
                 ) -> None:

        self.base_url = base_url.rstrip("/")
        headers = {"Accept": "application/json"}
        if default_headers:
            headers.update(default_headers)

        self._client = httpx.Client(
            base_url=self.base_url,
            timeout=timeout,
            headers=headers
        )

    def request(self,
                method: str,
                path: str,
                *,
                params: Mapping[str, Any] | None = None,
                json_body: Any | None = None,
                headers: Mapping[str, str] | None = None) -> httpx.Response:
        """发送请求并记录请求与响应的关键信息。"""
        normalized_path = f"/{path.lstrip('/')}"
        method = method.upper()
        started_at = perf_counter()

        logger.info(
            "API request %s %s%s",
            method,
            self.base_url,
            normalized_path
        )

        request_options: dict[str, Any] = {}
        if params is not None:
            request_options["params"] = params
        if json_body is not None:
            request_options["json"] = json_body
        if headers is not None:
            request_options["headers"] = dict(headers)

        try:
            response = self._client.request(
                method,
                normalized_path,
                **request_options,
            )
        except httpx.HTTPError:
            logger.exception(
                "API request failed %s %s%s",
                method,
                self.base_url,
                normalized_path,
            )
            raise
        elapsed_ms = (perf_counter() - started_at) * 1000
        logger.info(
            "API response %s %s -> %s (%.2f ms)",
            method,
            response.request.url,
            response.status_code,
            elapsed_ms,
        )
        return response

    def get(self,
            path: str,
            *,
            params: Mapping[str, Any] | None = None,
            headers: Mapping[str, str] | None = None, ) -> httpx.Response:
        return self.request("GET", path, params=params, headers=headers)

    def post(self,
             path: str,
             *,
             json_body: Any | None = None,
             params: Mapping[str, Any] | None = None,
             headers: Mapping[str, str] | None = None,
             ) -> httpx.Response:
        return self.request("POST", path=path, params=params, json_body=json_body, headers=headers)

    def put(self,
            path: str,
            *,
            json_body: Any | None = None,
            params: Mapping[str, Any] | None = None,
            headers: Mapping[str, str] | None = None,
            ) -> httpx.Response:
        return self.request(
            "PUT",
            path,
            params=params,
            json_body=json_body,
            headers=headers,
        )

    def delete(
            self,
            path: str,
            *,
            params: Mapping[str, Any] | None = None,
            headers: Mapping[str, str] | None = None,
    ) -> httpx.Response:
        return self.request("DELETE", path, params=params, headers=headers)


    def close(self) -> None:
        """关闭底层连接池。"""
        self._client.close()

    def __enter__(self) -> "APIClient":
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.close()