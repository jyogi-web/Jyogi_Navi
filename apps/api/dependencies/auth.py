"""認証・認可の FastAPI 依存関数。"""

import logging

from fastapi import Depends, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import User, UserRole
from db.session import get_db_session
from services.jwt_utils import COOKIE_NAME, decode_access_token

logger = logging.getLogger(__name__)


class AuthError(Exception):
    def __init__(self, status_code: int, detail: str) -> None:
        self.status_code = status_code
        self.detail = detail


async def get_current_user(
    request: Request,
    session: AsyncSession = Depends(get_db_session),
) -> User:
    """Cookie の JWT を検証して User を返す。失敗時は 401 を送出する。"""
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        raise AuthError(401, "Not authenticated")

    try:
        payload = decode_access_token(token)
    except ValueError as err:
        raise AuthError(401, "Invalid or expired token") from err

    user_id: str = payload.get("sub", "")
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise AuthError(401, "User not found")

    return user


async def require_member(user: User = Depends(get_current_user)) -> User:
    """MEMBER 以上のロール (MEMBER または ADMIN) を要求する。"""
    if user.role not in (UserRole.MEMBER, UserRole.ADMIN):
        raise AuthError(403, "Forbidden")
    return user


async def require_admin(user: User = Depends(get_current_user)) -> User:
    """ADMIN ロールのみ許可する。"""
    if user.role != UserRole.ADMIN:
        raise AuthError(403, "Forbidden")
    return user
