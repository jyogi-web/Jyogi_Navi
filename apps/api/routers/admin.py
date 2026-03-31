from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import User
from db.session import get_db_session
from dependencies.auth import require_member
from schemas.admin import AdminStatsResponse, FeedbackListResponse
from services.stats import get_admin_stats, get_feedback_list

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/stats", response_model=AdminStatsResponse)
async def admin_stats(
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_member),
) -> AdminStatsResponse:
    """管理ダッシュボード用KPI集計エンドポイント。"""
    return await get_admin_stats(session)


@router.get("/feedbacks", response_model=FeedbackListResponse)
async def feedback_list(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_member),
) -> FeedbackListResponse:
    """フィードバック一覧を返す。"""
    return await get_feedback_list(session, limit=limit, offset=offset)
