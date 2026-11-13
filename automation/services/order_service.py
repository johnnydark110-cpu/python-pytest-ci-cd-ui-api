"""订单创建、查询、修改与删除的业务服务。"""

from __future__ import annotations

from typing import Any

import httpx

from core import APIClient


class OrderService:
    """封装被测系统的订单业务接口。"""

    ORDERS_PATH = "/api/orders"

    def __init__(self, api_client: APIClient, token: str) -> None:
        normalized_token = token.strip()
        if not normalized_token:
            raise ValueError("订单服务需要非空 token")

        self.api_client = api_client
        self.token = normalized_token

    def create_order(
        self,

        title: str,
        amount: float,
        status: str = "pending",
    ) -> httpx.Response:
        """创建订单并返回原始响应。"""
        return self.api_client.post(
            self.ORDERS_PATH,
            json_body={
                "title": title,
                "amount": amount,
                "status": status,
            },
            headers=self._auth_headers(),
        )

    def get_order(self, order_id: int) -> httpx.Response:
        """获取指定订单详情。"""
        return self.api_client.get(
            self._order_path(order_id),
            headers=self._auth_headers(),
        )

    def list_orders(
        self,
        *,
        page: int = 1,
        page_size: int = 10,
        query: str | None = None,
    ) -> httpx.Response:
        """分页查询订单，可按标题搜索。"""
        params: dict[str, Any] = {
            "page": page,
            "page_size": page_size,
        }
        if query:
            params["q"] = query

        return self.api_client.get(
            self.ORDERS_PATH,
            params=params,
            headers=self._auth_headers(),
        )

    def update_order(
        self,
        order_id: int,
        *,
        title: str | None = None,
        amount: float | None = None,
        status: str | None = None,
    ) -> httpx.Response:
        """按提供的字段修改订单，未提供字段不发送。"""
        payload = {
            key: value
            for key, value in {
                "title": title,
                "amount": amount,
                "status": status,
            }.items()
            if value is not None
        }

        return self.api_client.put(
            self._order_path(order_id),
            json_body=payload,
            headers=self._auth_headers(),
        )

    def delete_order(self, order_id: int) -> httpx.Response:
        """删除指定订单。"""
        return self.api_client.delete(
            self._order_path(order_id),
            headers=self._auth_headers(),
        )

    def _auth_headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.token}",
        }

    def _order_path(self, order_id: int) -> str:
        return f"{self.ORDERS_PATH}/{order_id}"