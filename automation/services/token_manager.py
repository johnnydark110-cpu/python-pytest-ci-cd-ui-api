"""token 缓存、有效性和刷新管理。"""

from __future__ import annotations

from collections.abc import Callable

from .auth_service import AuthService


class TokenManager:
    """为单个测试用户管理 token 生命周期。"""

    def __init__(
        self,
        auth_service: AuthService,
        *,
        username: str,
        password: str,
        validator: Callable[[str], bool],
    ) -> None:
        self.auth_service = auth_service
        self.username = username
        self.password = password
        self.validator = validator
        self._token: str | None = None
        self.login_count = 0

    @property
    def cached_token(self) -> str | None:
        """返回当前缓存 token，不执行有效性检查。"""
        return self._token

    @property
    def has_cached_token(self) -> bool:
        """当前是否持有缓存 token。"""
        return self._token is not None

    def invalidate(self) -> None:
        """丢弃缓存 token，下一次获取会重新登录。"""
        self._token = None

    def get_valid_token(self, *, force_refresh: bool = False) -> str:
        """返回有效 token；必要时重新登录刷新。"""
        if (
            not force_refresh
            and self._token is not None
            and self.validator(self._token)
        ):
            return self._token

        return self.refresh()

    def refresh(self) -> str:
        """重新登录并替换缓存 token。"""
        token = self.auth_service.get_token(
            username=self.username,
            password=self.password,
        )
        self._token = token
        self.login_count += 1
        return token
