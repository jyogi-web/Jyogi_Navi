from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_db_session
from schemas.feedback import FeedbackCreate, FeedbackResponse
from services import log_store

router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.post("", response_model=FeedbackResponse, status_code=201)
async def send_feedback(
    body: FeedbackCreate,
    db: AsyncSession = Depends(get_db_session),
) -> FeedbackResponse:
    """フィードバック(👍👎)を保存する。"""
    feedback = await log_store.save_feedback(db, body)
    return FeedbackResponse.model_validate(feedback)
