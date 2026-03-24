from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from services.log_store import get_daily_token_usage


async def is_rate_limited(session: AsyncSession, session_id: str) -> bool:
    """当日使用量が上限を超えている場合 True を返す。"""
    used = await get_daily_token_usage(session, session_id)
    return used >= settings.daily_token_limit
