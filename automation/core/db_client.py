"""SQLite 测试数据校验与清理客户端。"""

from __future__ import annotations

import sqlite3
from contextlib import closing
from pathlib import Path


class DBClient:
    """直接执行测试数据库查询与清理。"""

    def __init__(
        self,
        database_path: str | Path,
        *,
        timeout_seconds: float = 15.0,
    ) -> None:
        self.database_path = Path(database_path)
        self.timeout_seconds = timeout_seconds

        if not self.database_path.is_file():
            raise FileNotFoundError(f"测试数据库不存在: {self.database_path}")

    def _connect(self) -> sqlite3.Connection:
        """创建独立数据库连接并设置锁等待时间。"""
        connection = sqlite3.connect(
            self.database_path,
            timeout=self.timeout_seconds,
        )
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute(f"PRAGMA busy_timeout = {int(self.timeout_seconds * 1000)}")
        return connection

    def user_exists(self, username: str) -> bool:
        """判断用户名是否存在。"""
        with closing(self._connect()) as connection:
            row = connection.execute(
                "SELECT 1 FROM users WHERE username = ?",
                (username,),
            ).fetchone()

        return row is not None

    def session_exists(self, token: str) -> bool:
        """判断登录 session 是否存在。"""
        with closing(self._connect()) as connection:
            row = connection.execute(
                "SELECT 1 FROM sessions WHERE token = ?",
                (token,),
            ).fetchone()

        return row is not None

    def order_exists(self, order_id: int) -> bool:
        """判断订单是否存在。"""
        with closing(self._connect()) as connection:
            row = connection.execute(
                "SELECT 1 FROM orders WHERE id = ?",
                (order_id,),
            ).fetchone()

        return row is not None

    def delete_user_by_username(self, username: str) -> bool:
        """删除用户及其 session 和关联订单。"""
        with closing(self._connect()) as connection, connection:
            user = connection.execute(
                "SELECT id FROM users WHERE username = ?",
                (username,),
            ).fetchone()

            if user is None:
                return False

            user_id = user["id"]

            connection.execute(
                "DELETE FROM sessions WHERE user_id = ?",
                (user_id,),
            )
            connection.execute(
                "DELETE FROM orders WHERE user_id = ?",
                (user_id,),
            )
            connection.execute(
                "DELETE FROM users WHERE id = ?",
                (user_id,),
            )

        return True
