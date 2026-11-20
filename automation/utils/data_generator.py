"""动态测试数据生成。"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from uuid import uuid4

from faker import Faker

ORDER_STATUSES = (
    "pending",
    "paid",
    "shipped",
    "done",
    "canceled",
)

USERNAME_MIN_LENGTH = 3
USERNAME_MAX_LENGTH = 32
PASSWORD_MIN_LENGTH = 6
PASSWORD_MAX_LENGTH = 64
ORDER_TITLE_MIN_LENGTH = 1
ORDER_TITLE_MAX_LENGTH = 100


@dataclass(frozen=True, slots=True)
class UserData:
    """注册与登录使用的用户数据。"""

    username: str
    password: str = field(repr=False)


@dataclass(frozen=True, slots=True)
class OrderData:
    """创建订单使用的业务数据。"""

    title: str
    amount: float
    status: str


class TestDataFactory:
    """生成符合被测系统约束的随机测试数据。"""

    def __init__(self, *, locale: str = "zh_CN") -> None:
        self.faker = Faker(locale)

    def user(self, *, prefix: str = "api") -> UserData:
        """生成唯一用户。"""
        username = f"{prefix}_{uuid4().hex[:12]}"

        if not (USERNAME_MIN_LENGTH <= len(username) <= USERNAME_MAX_LENGTH):
            raise ValueError(f"用户名长度不合法: {username}")

        password = self.faker.password(
            length=16,
            special_chars=False,
            digits=True,
            upper_case=True,
            lower_case=True,
        )

        if not (PASSWORD_MIN_LENGTH <= len(password) <= PASSWORD_MAX_LENGTH):
            raise ValueError("生成的密码长度不合法")

        return UserData(
            username=username,
            password=password,
        )

    def order(
        self,
        *,
        title: str | None = None,
        amount: float | None = None,
        status: str | None = None,
    ) -> OrderData:
        """生成合法订单数据，也允许测试显式覆盖字段。"""
        resolved_title = title if title is not None else self._unique_order_title()

        if not (
            ORDER_TITLE_MIN_LENGTH <= len(resolved_title) <= ORDER_TITLE_MAX_LENGTH
        ):
            raise ValueError("订单标题长度必须在 1 到 100 之间")

        resolved_amount = (
            float(amount)
            if amount is not None
            else round(
                self.faker.pyfloat(
                    min_value=0.01,
                    max_value=9999.99,
                    right_digits=2,
                ),
                2,
            )
        )

        if resolved_amount <= 0:
            raise ValueError("订单金额必须大于 0")

        resolved_status = (
            status if status is not None else random.choice(ORDER_STATUSES)
        )

        if resolved_status not in ORDER_STATUSES:
            raise ValueError(f"不支持的订单状态: {resolved_status}")

        return OrderData(
            title=resolved_title,
            amount=resolved_amount,
            status=resolved_status,
        )

    def _unique_order_title(self) -> str:
        """生成带 UUID 的唯一订单标题。"""
        suffix = uuid4().hex[:10]
        word = self.faker.word().strip() or "order"
        title = f"auto-{suffix}-{word}"

        return title[:ORDER_TITLE_MAX_LENGTH]
