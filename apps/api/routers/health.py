from fastapi import APIRouter
from pydantic import BaseModel

from services.log_store import ping

router = APIRouter(tags=["health"])

class HealthResponse(BaseModel):
    status: str
    db: str

@router.get("/health", response_model=HealthResponse)
def health_check():
    """サービスの死活監視エンドポイント。"""
    db_status = "ok" if ping() else "unreachable"
    return HealthResponse(status="ok", db=db_status)
