"""注册与登录接口。"""

from fastapi import APIRouter, HTTPException, status

from .. import auth as auth_helpers
from .. import database, security
from ..schemas import AuthResponse, LoginRequest, RegisterRequest

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post(
    "/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED
)
def register(payload: RegisterRequest) -> AuthResponse:
    conn = database.get_connection()
    exists = conn.execute(
        "SELECT id FROM users WHERE username = ?", (payload.username,)
    ).fetchone()
    if exists:
        conn.close()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="用户名已存在")
    cursor = conn.execute(
        "INSERT INTO users (username, password_hash, role) VALUES (?, ?, 'user')",
        (payload.username, security.hash_password(payload.password)),
    )
    conn.commit()
    token = auth_helpers.create_session(conn, cursor.lastrowid)
    conn.close()
    return AuthResponse(token=token, username=payload.username, role="user")


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest) -> AuthResponse:
    conn = database.get_connection()
    row = conn.execute(
        "SELECT id, username, password_hash, role FROM users WHERE username = ?",
        (payload.username,),
    ).fetchone()
    if row is None or not security.verify_password(
        payload.password, row["password_hash"]
    ):
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误"
        )
    token = auth_helpers.create_session(conn, row["id"])
    conn.close()
    return AuthResponse(token=token, username=row["username"], role=row["role"])
