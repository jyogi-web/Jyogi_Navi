"""Dify Chat API クライアント。"""

import json
from dataclasses import dataclass

import httpx

from config import settings
from exceptions import ExternalServiceError, InternalError


@dataclass
class DifyResponse:
    """Dify Chat API レスポンス。"""

    answer: str
    tokens_used: int


async def send_chat_message(
    session_id: str, message: str, trace_id: str = ""
) -> DifyResponse:
    """Dify Chat API にメッセージを送信して回答を返す。"""
    base_url = settings.dify_api_base_url.strip()
    api_key = settings.dify_api_key.get_secret_value().strip()
    if not base_url or not api_key:
        raise InternalError("DIFY_CONFIG_MISSING")

    base = base_url.rstrip("/")
    url = (
        f"{base}/chat-messages" if base.endswith("/v1") else f"{base}/v1/chat-messages"
    )
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    if trace_id:
        headers["X-Request-ID"] = trace_id
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
        raise ExternalServiceError("DIFY_CONN_TIMEOUT") from exc
    except httpx.HTTPStatusError as exc:
        raise ExternalServiceError("DIFY_HTTP_ERROR") from exc
    except httpx.RequestError as exc:
        raise ExternalServiceError("DIFY_UNREACHABLE") from exc

    try:
        data = response.json()
    except (json.JSONDecodeError, ValueError) as exc:
        raise ExternalServiceError("DIFY_INVALID_RESPONSE") from exc

    if not isinstance(data, dict):
        raise ExternalServiceError("DIFY_INVALID_RESPONSE")
    answer = data.get("answer", "")
    if not isinstance(answer, str):
        raise ExternalServiceError("DIFY_INVALID_RESPONSE")
    metadata = data.get("metadata", {})
    if not isinstance(metadata, dict):
        metadata = {}
    usage = metadata.get("usage", {})
    if not isinstance(usage, dict):
        usage = {}
    raw_tokens = usage.get("total_tokens", 0)
    try:
        tokens_used = max(0, int(raw_tokens))
    except (TypeError, ValueError) as exc:
        raise ExternalServiceError("DIFY_INVALID_RESPONSE") from exc

    return DifyResponse(answer=answer, tokens_used=tokens_used)
