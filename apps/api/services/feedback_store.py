"""フィードバック保存サービス。"""

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Feedback
from services.log_store import _emit_structured_log

logger = logging.getLogger(__name__)


async def save_feedback(
    session: AsyncSession,
    session_id: str,
    rating: str,
    comment: str | None,
    trace_id: str,
) -> Feedback:
    """feedbacks にフィードバックを保存する。"""
    feedback = Feedback(
        session_id=session_id,
        rating=rating,
        comment=comment,
    )
    session.add(feedback)
    await session.commit()
    await session.refresh(feedback)

    _emit_structured_log(
        level="INFO",
        action="feedback.submit",
        trace_id=trace_id,
        metadata={"session_id": session_id, "rating": rating},
    )
    return feedback
