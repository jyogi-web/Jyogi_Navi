import logging

from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from services.log_store import get_daily_token_usage

logger = logging.getLogger(__name__)


async def is_rate_limited(session: AsyncSession, session_id: str) -> bool:
    """当日使用量が上限を超えている場合 True を返す。

    DB障害時はレート制限をスキップする。
    """
    try:
        used = await get_daily_token_usage(session, session_id)
    except Exception:
        logger.exception("rate_limit check failed: session_id=%s", session_id)
        return False
    return used >= settings.daily_token_limit
