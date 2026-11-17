"""统一封装 HTTP 请求的基础 API 客户端。"""

from __future__ import annotations

from collections.abc import Mapping
from time import perf_counter
from types import TracebackType
from typing import Any, Self

import allure
import httpx

from .allure_utils import attach_redacted_json
from .exceptions import APITransportError
from .logger import format_log_data, get_logger
from .request_context import record_request_exchange

logger = get_logger(__name__)

DEFAULT_BASE_URL = "http://127.0.0.1:8000"
DEFAULT_TIMEOUT_SECONDS = 10.0


class APIClient:
    """为测试框架提供统一配置和请求日志的 HTTP 客户端。"""

    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float | httpx.Timeout = DEFAULT_TIMEOUT_SECONDS,
        default_headers: Mapping[str, str] | None = None,
        verify_ssl: bool = True,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.verify_ssl = verify_ssl

        headers = {"Accept": "application/json"}
        if default_headers:
            headers.update(default_headers)

        self._client = httpx.Client(
            base_url=self.base_url,
            timeout=timeout,
            headers=headers,
            verify=verify_ssl,
        )

    def request(
        self,
        method: str,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
        json_body: Any | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> httpx.Response:
        """发送请求并记录脱敏后的完整请求响应上下文。"""
        normalized_path = f"/{path.lstrip('/')}"
        method = method.upper()
        request_url = f"{self.base_url}{normalized_path}"
        started_at = perf_counter()

        effective_headers = dict(self._client.headers)
        if headers is not None:
            effective_headers.update(headers)

        request_context = {
            "method": method,
            "url": request_url,
            "params": params,
            "headers": effective_headers,
            "body": json_body,
        }
        # logger.info(
        #     "API request details:\n%s",
        #     format_log_data(request_context),
        # )

        request_options: dict[str, Any] = {}
        if params is not None:
            request_options["params"] = params
        if json_body is not None:
            request_options["json"] = json_body
        if headers is not None:
            request_options["headers"] = dict(headers)

        with allure.step(f"HTTP {method} {normalized_path}"):
            logger.info(
                "API request details:\n%s",
                format_log_data(request_context),
            )
            attach_redacted_json(
                name="请求上下文",
                data=request_context,
            )

            try:
                response = self._client.request(
                    method,
                    normalized_path,
                    **request_options,
                )
            except httpx.HTTPError as exc:
                logger.exception(
                    "API request failed %s %s",
                    method,
                    request_url,
                )
                record_request_exchange(
                    request_context,
                    {
                        "transport_error": {
                            "type": type(exc).__name__,
                            "message": str(exc),
                        }
                    },
                )
                raise APITransportError(
                    method=method,
                    url=request_url,
                    cause=exc,
                ) from exc

            elapsed_ms = (perf_counter() - started_at) * 1000
            logger.info(
                "API response %s %s -> %s (%.2f ms)",
                method,
                response.request.url,
                response.status_code,
                elapsed_ms,
            )

            response_context = {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "body": self._read_response_body(response),
                "elapsed_ms": round(elapsed_ms, 2),
            }
            logger.info(
                "API response details:\n%s",
                format_log_data(response_context),
            )
            attach_redacted_json(
                name="响应上下文",
                data=response_context,
            )
            record_request_exchange(
                request_context,
                response_context,
            )

        return response

    def get(
        self,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> httpx.Response:
        return self.request("GET", path, params=params, headers=headers)

    def post(
        self,
        path: str,
        *,
        json_body: Any | None = None,
        params: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> httpx.Response:
        return self.request(
            "POST",
            path,
            params=params,
            json_body=json_body,
            headers=headers,
        )

    def put(
        self,
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

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.close()

    @staticmethod
    def _read_response_body(response: httpx.Response) -> Any:
        """优先读取 JSON，非 JSON 响应则返回文本。"""
        try:
            return response.json()
        except ValueError:
            return response.text
