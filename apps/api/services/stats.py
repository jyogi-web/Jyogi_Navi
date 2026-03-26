"""管理ダッシュボード用KPI集計ロジック。"""

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Feedback, UsageLog
from schemas.admin import AdminStatsResponse, DailyCount


async def get_admin_stats(session: AsyncSession) -> AdminStatsResponse:
    """usage_logs と feedbacks を集計して管理KPIを返す。"""
    # 日別質問数
    daily_result = await session.execute(
        select(
            func.date(UsageLog.created_at).label("day"),
            func.count().label("count"),
        )
        .group_by(func.date(UsageLog.created_at))
        .order_by(func.date(UsageLog.created_at).desc())
    )
    daily_counts = [
        DailyCount(date=row.day, count=row.count) for row in daily_result.all()
    ]

    # 総トークン消費量
    total_result = await session.execute(select(func.sum(UsageLog.tokens)))
    total_tokens: int = total_result.scalar() or 0

    # 👍率
    good_rate_result = await session.execute(
        select(
            (
                func.count(case((Feedback.rating == "good", 1))) * 100.0 / func.count()
            ).label("good_rate")
        )
    )
    good_rate: float = good_rate_result.scalar() or 0.0

    return AdminStatsResponse(
        daily_counts=daily_counts,
        total_tokens=total_tokens,
        good_rate=round(good_rate, 1),
    )
