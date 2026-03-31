"""Discord OAuth2 認証サービス。"""

import logging

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from db.models import User, UserRole
from exceptions import AppError

logger = logging.getLogger(__name__)

DISCORD_API_BASE = "https://discord.com/api/v10"
DISCORD_TOKEN_URL = "https://discord.com/api/oauth2/token"
_DISCORD_TIMEOUT = httpx.Timeout(10.0)


async def exchange_code(code: str) -> str:
    """認可コードを Discord アクセストークンに交換する。"""
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": settings.discord_redirect_uri,
        "client_id": settings.discord_client_id,
        "client_secret": settings.discord_client_secret.get_secret_value(),
    }
    async with httpx.AsyncClient(timeout=_DISCORD_TIMEOUT) as client:
        response = await client.post(
            DISCORD_TOKEN_URL,
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
    if response.status_code != 200:
        logger.error("Discord token exchange failed: %s", response.text)
        raise AppError(502, "DISCORD_TOKEN_ERROR", "Discord 認証に失敗しました")
    return response.json()["access_token"]


async def get_discord_user(access_token: str) -> dict:
    """Discord ユーザー情報 (id, username) を取得する。"""
    async with httpx.AsyncClient(timeout=_DISCORD_TIMEOUT) as client:
        response = await client.get(
            f"{DISCORD_API_BASE}/users/@me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
    if response.status_code != 200:
        logger.error("Discord get user failed: %s", response.text)
        raise AppError(
            502, "DISCORD_USER_ERROR", "Discord ユーザー情報の取得に失敗しました"
        )
    return response.json()


async def check_guild_member(access_token: str) -> bool:
    """じょぎ Discord サーバーのメンバーかどうかを確認する。"""
    guild_id = settings.discord_guild_id
    async with httpx.AsyncClient(timeout=_DISCORD_TIMEOUT) as client:
        response = await client.get(
            f"{DISCORD_API_BASE}/users/@me/guilds/{guild_id}/member",
            headers={"Authorization": f"Bearer {access_token}"},
        )
    # 200 = メンバー, 404 = 非メンバー
    return response.status_code == 200


async def upsert_user(
    session: AsyncSession, discord_user_id: str, user_name: str
) -> User:
    """DB に users レコードを作成する。

    既存ユーザーの場合は role を維持し user_name を更新する。
    """
    import uuid

    result = await session.execute(
        select(User).where(User.discord_user_id == discord_user_id)
    )
    user = result.scalar_one_or_none()
    if user is None:
        user = User(
            id=str(uuid.uuid4()),
            discord_user_id=discord_user_id,
            user_name=user_name,
            role=UserRole.MEMBER,
        )
        session.add(user)
    else:
        user.user_name = user_name
    await session.commit()
    await session.refresh(user)
    return user
