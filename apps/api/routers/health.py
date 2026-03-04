from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_db_session
from services.log_store import ping

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    status: str
    db: str


@router.get("/health", response_model=HealthResponse)
async def health_check(session: AsyncSession = Depends(get_db_session)):
    """サービスの死活監視エンドポイント。"""
    db_ok = await ping(session)
    db_status = "ok" if db_ok else "unreachable"
    status = "ok" if db_ok else "degraded"
    response = HealthResponse(status=status, db=db_status)
    http_status = 200 if db_ok else 503
    return JSONResponse(content=response.model_dump(), status_code=http_status)
