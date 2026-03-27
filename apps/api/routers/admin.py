from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import User
from db.session import get_db_session
from dependencies.auth import require_member
from schemas.admin import AdminStatsResponse
from services.stats import get_admin_stats

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/stats", response_model=AdminStatsResponse)
async def admin_stats(
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_member),
) -> AdminStatsResponse:
    """管理ダッシュボード用KPI集計エンドポイント。"""
    return await get_admin_stats(session)
