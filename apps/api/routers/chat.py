import logging

from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Session as SessionModel
from db.session import get_db_session
from exceptions import RateLimitExceeded
from schemas.chat import ChatRequest, ChatResponse
from services.dify_client import send_chat_message
from services.log_store import check_and_save_usage_log
from services.pii_mask import mask
from services.rate_limit import is_rate_limited

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(
    body: ChatRequest,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
) -> ChatResponse:
    """Dify Chat API を呼び出してLLMの回答を返すエンドポイント。"""
    trace_id: str = getattr(request.state, "trace_id", "")

    if await is_rate_limited(session, body.session_id):
        raise RateLimitExceeded()

    masked_message = mask(body.message)
    dify_response = await send_chat_message(body.session_id, masked_message, trace_id)
    masked_answer = mask(dify_response.answer)

    try:
        # sessions テーブルに該当行がなければ作成(consentエンドポイント実装前の暫定対応)
        result = await session.execute(
            select(SessionModel).where(SessionModel.id == body.session_id)
        )
        if result.scalar_one_or_none() is None:
            try:
                session.add(
                    SessionModel(id=body.session_id, is_guest=True, consented=True)
                )
                await session.flush()
            except IntegrityError:
                # 同一 session_id の並列リクエストによる競合は無害
                logger.debug(
                    "session already exists (race): session_id=%s", body.session_id
                )
                await session.rollback()

        await check_and_save_usage_log(
            session=session,
            session_id=body.session_id,
            tokens=dify_response.tokens_used,
            trace_id=trace_id,
        )
    except RateLimitExceeded:
        raise
    except Exception:
        logger.exception(
            "usage_log save failed: session_id=%s trace_id=%s",
            body.session_id,
            trace_id,
        )

    return ChatResponse(answer=masked_answer, tokens_used=dify_response.tokens_used)
