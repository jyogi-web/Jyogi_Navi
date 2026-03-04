from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

# TODO: ログ保存の実装(P1)


async def ping(session: AsyncSession) -> bool:
    """DB疎通確認。ヘルスチェックに使用。"""
    try:
        await session.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
