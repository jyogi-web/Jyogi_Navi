"""JWT 生成・検証ユーティリティ。"""

from datetime import UTC, datetime, timedelta

import jwt

from config import settings
from db.models import User

ALGORITHM = "HS256"
COOKIE_NAME = "admin_token"


def create_access_token(user: User) -> str:
    """ユーザー情報から JWT を生成する。"""
    expire = datetime.now(UTC) + timedelta(minutes=settings.jwt_expire_minutes)
    payload = {
        "sub": user.id,
        "discord_user_id": user.discord_user_id,
        "role": user.role.value,
        "exp": expire,
    }
    return jwt.encode(
        payload,
        settings.jwt_secret.get_secret_value(),
        algorithm=ALGORITHM,
    )


def decode_access_token(token: str) -> dict:
    """JWT を検証してペイロードを返す。無効な場合は ValueError を送出する。"""
    try:
        return jwt.decode(
            token,
            settings.jwt_secret.get_secret_value(),
            algorithms=[ALGORITHM],
        )
    except jwt.ExpiredSignatureError as exc:
        raise ValueError("Token expired") from exc
    except jwt.InvalidTokenError as exc:
        raise ValueError("Invalid token") from exc
