from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_db_session
from schemas.session import UsageLogCreate, UsageLogResponse
from services.log_store import save_usage_log

router = APIRouter(prefix="/usage-logs", tags=["usage-logs"])


@router.post("", response_model=UsageLogResponse, status_code=201)
async def create_usage_log(
    body: UsageLogCreate,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
) -> UsageLogResponse:
    """チャットAPIから呼ばれるトークン消費ログ保存エンドポイント。"""
    trace_id: str = getattr(request.state, "trace_id", "")
    log = await save_usage_log(
        session=session,
        session_id=body.session_id,
        tokens=body.tokens,
        trace_id=trace_id,
        category=body.category,
    )
    return UsageLogResponse.model_validate(log)
