import logging

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_db_session
from schemas.feedback import FeedbackCreate, FeedbackResponse
from services.feedback_store import save_feedback

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/feedback", tags=["feedback"])


@router.post("", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
async def create_feedback(
    body: FeedbackCreate,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
) -> FeedbackResponse:
    """チャット回答への👍/👎フィードバックを保存するエンドポイント。"""
    trace_id: str = getattr(request.state, "trace_id", "")

    feedback = await save_feedback(
        session=session,
        session_id=body.session_id,
        rating=body.rating,
        comment=body.comment,
        trace_id=trace_id,
    )

    return FeedbackResponse.model_validate(feedback)
