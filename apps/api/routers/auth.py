"""Discord OAuth2 認証ルーター。"""

import logging
import urllib.parse

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from db.models import User
from db.session import get_db_session
from dependencies.auth import require_member
from schemas.auth import UserResponse
from services.discord_auth import (
    check_guild_member,
    exchange_code,
    get_discord_user,
    upsert_user,
)
from services.jwt_utils import COOKIE_NAME, create_access_token

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["auth"])

DISCORD_OAUTH_URL = "https://discord.com/oauth2/authorize"
# guilds: ユーザーが参加しているギルド一覧を取得する
# guilds.members.read: 特定ギルドのメンバー詳細 (ロール・ニックネーム等) を取得する
# 両スコープは独立しており、いずれも必要
SCOPES = "identify guilds guilds.members.read"

ADMIN_FRONTEND_URL = settings.admin_frontend_url


@router.get("/login")
async def login() -> RedirectResponse:
    """Discord OAuth 認可画面にリダイレクトする。"""
    params = urllib.parse.urlencode(
        {
            "client_id": settings.discord_client_id,
            "redirect_uri": settings.discord_redirect_uri,
            "response_type": "code",
            "scope": SCOPES,
        }
    )
    return RedirectResponse(url=f"{DISCORD_OAUTH_URL}?{params}")


@router.get("/callback")
async def callback(
    code: str,
    session: AsyncSession = Depends(get_db_session),
) -> RedirectResponse:
    """Discord OAuth コールバック。トークンを交換してセッション Cookie を発行する。"""
    access_token = await exchange_code(code)

    discord_user = await get_discord_user(access_token)
    discord_user_id: str = discord_user["id"]

    is_member = await check_guild_member(access_token)
    if not is_member:
        return RedirectResponse(url=f"{ADMIN_FRONTEND_URL}/login?error=not_member")

    user = await upsert_user(session, discord_user_id)
    jwt_token = create_access_token(user)

    response = RedirectResponse(url=f"{ADMIN_FRONTEND_URL}/dashboard")
    response.set_cookie(
        key=COOKIE_NAME,
        value=jwt_token,
        httponly=True,
        samesite="lax",
        max_age=settings.jwt_expire_minutes * 60,
        secure=settings.jwt_cookie_secure,
    )
    return response


@router.get("/me", response_model=UserResponse)
async def me(user: User = Depends(require_member)) -> User:
    """現在ログイン中のユーザー情報を返す。"""
    return user


@router.post("/logout")
async def logout() -> JSONResponse:
    """Cookie を削除してログアウトする。"""
    response = JSONResponse(content={"ok": True})
    response.delete_cookie(
        key=COOKIE_NAME,
        httponly=True,
        samesite="lax",
        secure=settings.jwt_cookie_secure,
    )
    return response
