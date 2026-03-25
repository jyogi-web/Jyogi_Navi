"""Dify Chat API クライアント。"""

import json
from dataclasses import dataclass

import httpx
from fastapi import HTTPException

from config import settings


@dataclass
class DifyResponse:
    """Dify Chat API レスポンス。"""

    answer: str
    tokens_used: int


async def send_chat_message(session_id: str, message: str) -> DifyResponse:
    """Dify Chat API にメッセージを送信して回答を返す。"""
    api_key = settings.dify_api_key.get_secret_value().strip()
    if not settings.dify_api_base_url.strip() or not api_key:
        raise HTTPException(status_code=500, detail="Dify API configuration missing")

    base = settings.dify_api_base_url.rstrip("/")
    url = (
        f"{base}/chat-messages" if base.endswith("/v1") else f"{base}/v1/chat-messages"
    )
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "inputs": {},
        "query": message,
        "user": session_id,
        "response_mode": "blocking",
    }

    try:
        async with httpx.AsyncClient(timeout=settings.dify_timeout_seconds) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
    except httpx.TimeoutException as exc:
        raise HTTPException(status_code=504, detail="upstream timeout") from exc
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=502, detail="upstream error") from exc
    except httpx.RequestError as exc:
        raise HTTPException(status_code=502, detail="upstream unreachable") from exc

    try:
        data = response.json()
    except (json.JSONDecodeError, ValueError) as exc:
        raise HTTPException(
            status_code=502, detail="upstream returned invalid response"
        ) from exc

    answer = data.get("answer", "")
    raw_tokens = data.get("metadata", {}).get("usage", {}).get("total_tokens", 0)
    try:
        tokens_used = max(0, int(raw_tokens))
    except (TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=502, detail="upstream returned invalid token usage"
        ) from exc

    return DifyResponse(answer=answer, tokens_used=tokens_used)
