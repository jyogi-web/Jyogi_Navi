"""FAQ検索エンドポイント。"""

import logging

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_db_session
from schemas.faq import FaqSearchResponse, FaqSearchResult
from services.faq_search import search_faq_by_keyword

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/faq", tags=["faq"])


@router.get("/search", response_model=FaqSearchResponse)
async def search_faq(
    request: Request,
    q: str = Query(min_length=1, max_length=200, description="検索キーワード"),
    session: AsyncSession = Depends(get_db_session),
) -> FaqSearchResponse:
    """FAQをキーワードで検索するエンドポイント(P0: LIKE検索)。"""
    trace_id: str = getattr(request.state, "trace_id", "")
    logger.info("faq_search: q_len=%d trace_id=%s", len(q), trace_id)

    rows = await search_faq_by_keyword(session, q)
    return FaqSearchResponse(
        results=[FaqSearchResult(content=row.content) for row in rows]
    )
