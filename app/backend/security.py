"""密码哈希与令牌工具，仅依赖 Python 标准库。"""

import hashlib
import hmac
import secrets


def hash_password(password: str) -> str:
    """使用 PBKDF2 对密码加盐哈希，返回 "salt$hex_digest"。"""
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100_000
    )
    return f"{salt}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    """校验明文密码是否与存储的哈希一致，使用恒定时间比较避免时序攻击。"""
    try:
        salt, expected = stored.split("$", 1)
    except ValueError:
        return False
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100_000
    )
    return hmac.compare_digest(digest.hex(), expected)


def generate_token() -> str:
    """生成随机会话令牌。"""
    return secrets.token_hex(32)
