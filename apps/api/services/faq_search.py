"""FAQ LIKE 検索サービス(P0: 暫定実装)。

P1 でベクトル検索に置き換え予定。
"""

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import FaqEmbedding

logger = logging.getLogger(__name__)

FAQ_SEARCH_LIMIT = 10


async def search_faq_by_keyword(
    session: AsyncSession,
    keyword: str,
    limit: int = FAQ_SEARCH_LIMIT,
) -> list[FaqEmbedding]:
    """content カラムに対して LIKE 検索を行い、上位 limit 件を返す。

    SQLAlchemy のパラメータ化クエリにより SQL インジェクションは防止される。
    空文字またはホワイトスペースのみのキーワードは空リストを返す。
    """
    if not keyword.strip():
        return []

    stmt = (
        select(FaqEmbedding)
        .where(FaqEmbedding.content.contains(keyword))
        .order_by(FaqEmbedding.created_at.desc())
        .limit(limit)
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())
