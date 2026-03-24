from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_db_session
from schemas.session import (
    SessionCreate,
    SessionResponse,
    UsageLogCreate,
    UsageLogResponse,
)
from services import log_store

router = APIRouter(prefix="/consent", tags=["consent"])


@router.post("/sessions", response_model=SessionResponse, status_code=201)
async def create_session(
    body: SessionCreate,
    db: AsyncSession = Depends(get_db_session),
) -> SessionResponse:
    """新しいセッションを作成する。"""
    session = await log_store.create_session(db, body)
    return SessionResponse.model_validate(session)


@router.post("/usage_logs", response_model=UsageLogResponse, status_code=201)
async def save_usage_log(
    body: UsageLogCreate,
    db: AsyncSession = Depends(get_db_session),
) -> UsageLogResponse:
    """トークン消費ログを保存する。"""
    log = await log_store.save_usage_log(db, body)
    return UsageLogResponse.model_validate(log)
