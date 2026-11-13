"""请求与响应的 Pydantic 模型，也是 API 的输入校验与输出结构。"""

from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=32)
    password: str = Field(min_length=6, max_length=64)


class LoginRequest(BaseModel):
    username: str
    password: str


class AuthResponse(BaseModel):
    token: str
    username: str
    role: str


class OrderCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    amount: float = Field(gt=0)
    status: str = Field(
        default="pending", pattern="^(pending|paid|shipped|done|canceled)$"
    )


class OrderUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    amount: float | None = Field(default=None, gt=0)
    status: str | None = Field(
        default=None, pattern="^(pending|paid|shipped|done|canceled)$"
    )


class OrderOut(BaseModel):
    id: int
    title: str
    amount: float
    status: str
    created_at: str


class OrderList(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[OrderOut]
