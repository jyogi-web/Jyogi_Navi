from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import UsageLog
from db.session import get_db_session
from schemas.admin import AdminStatsResponse, DailyCount

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/stats", response_model=AdminStatsResponse)
async def get_admin_stats(
    session: AsyncSession = Depends(get_db_session),
) -> AdminStatsResponse:
    """管理ダッシュボード用KPI集計エンドポイント。"""
    # 日別質問数
    daily_result = await session.execute(
        select(
            func.date(UsageLog.created_at).label("day"),
            func.count().label("count"),
        )
        .group_by(func.date(UsageLog.created_at))
        .order_by(func.date(UsageLog.created_at).desc())
    )
    daily_questions = [
        DailyCount(day=row.day, count=row.count) for row in daily_result.all()
    ]

    # 総トークン消費量
    total_result = await session.execute(select(func.sum(UsageLog.tokens)))
    total_tokens: int = total_result.scalar() or 0

    return AdminStatsResponse(
        daily_questions=daily_questions,
        total_tokens=total_tokens,
    )
