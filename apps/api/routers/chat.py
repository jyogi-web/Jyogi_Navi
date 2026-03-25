from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_db_session
from schemas.chat import ChatRequest, ChatResponse
from services.dify_client import send_chat_message
from services.log_store import save_usage_log
from services.pii_mask import mask
from services.rate_limit import is_rate_limited

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
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    masked_message = mask(body.message)
    dify_response = await send_chat_message(body.session_id, masked_message)
    masked_answer = mask(dify_response.answer)

    await save_usage_log(
        session=session,
        session_id=body.session_id,
        tokens=dify_response.tokens_used,
        trace_id=trace_id,
    )

    return ChatResponse(answer=masked_answer, tokens_used=dify_response.tokens_used)
