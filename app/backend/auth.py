"""会话令牌的创建与当前用户的鉴权依赖。"""

import sqlite3

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from . import database, security

_bearer = HTTPBearer(auto_error=False)


def create_session(conn: sqlite3.Connection, user_id: int) -> str:
    """为用户创建会话并返回令牌。"""
    token = security.generate_token()
    conn.execute("INSERT INTO sessions (token, user_id) VALUES (?, ?)", (token, user_id))
    conn.commit()
    return token


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> dict:
    """从 Authorization: Bearer <token> 解析当前登录用户。"""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未登录：请携带 Authorization: Bearer <token>",
        )
    conn = database.get_connection()
    row = conn.execute(
        """
        SELECT u.id, u.username, u.role
        FROM sessions s
        JOIN users u ON u.id = s.user_id
        WHERE s.token = ?
        """,
        (credentials.credentials,),
    ).fetchone()
    conn.close()
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="登录已失效，请重新登录",
        )
    return {"id": row["id"], "username": row["username"], "role": row["role"]}
