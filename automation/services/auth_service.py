"""注册、登录与 token 获取的业务服务。"""

from __future__ import annotations

from typing import Any

import httpx

from core import APIClient, APIResponseError


class AuthService:
    """封装被测系统的鉴权接口。"""

    REGISTER_PATH = "/api/auth/register"
    LOGIN_PATH = "/api/auth/login"

    def __init__(self, api_client: APIClient) -> None:
        self.api_client = api_client

    def register(
            self,
            username: str,
            password: str,
    ) -> httpx.Response:
        """调用注册接口并返回原始响应。"""
        return self.api_client.post(
            self.REGISTER_PATH,
            json_body={
                "username": username,
                "password": password,
            },
        )

    def login(
            self,
            username: str,
            password: str,
    ) -> httpx.Response:
        """调用登录接口并返回原始响应。"""
        return self.api_client.post(
            self.LOGIN_PATH,
            json_body={
                "username": username,
                "password": password,
            },
        )

    def get_token(
            self,
            username: str,
            password: str,
    ) -> str:
        """登录成功时必须返回可用 token。"""
        response = self.login(username, password)
        body = self._read_response_body(response)

        if response.status_code != 200:
            raise APIResponseError(
                f"登录失败，无法获取 token: status={response.status_code}",
                method="POST",
                url=str(response.request.url),
                status_code=response.status_code,
                body=body,
            )

        if not isinstance(body, dict):
            raise APIResponseError(
                "登录响应不是 JSON 对象",
                method="POST",
                url=str(response.request.url),
                status_code=response.status_code,
                body=body,
            )

        token = body.get("token")
        if not isinstance(token, str) or not token:
            raise APIResponseError(
                "登录成功响应中缺少有效 token",
                method="POST",
                url=str(response.request.url),
                status_code=response.status_code,
                body=body,
            )

        return token

    @staticmethod
    def _read_response_body(response: httpx.Response) -> Any:
        try:
            return response.json()
        except ValueError:
            return response.text
