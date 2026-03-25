"""グローバル例外ハンドラのテスト。"""

from unittest.mock import AsyncMock, patch

import pytest

from exceptions import ExternalServiceError


async def test_RateLimitExceededで429と日本語メッセージを返す(client):
    with patch("routers.chat.is_rate_limited", new=AsyncMock(return_value=True)):
        response = await client.post(
            "/api/chat",
            json={"session_id": "session-1", "message": "テスト"},
        )

    assert response.status_code == 429
    data = response.json()
    assert data["error_code"] == "RATE_LIMIT_EXCEEDED"
    assert data["message"] == "本日の質問上限に達しました"
    assert "trace_id" in data


async def test_ExternalServiceErrorで503と日本語メッセージを返す(client):
    with (
        patch("routers.chat.is_rate_limited", new=AsyncMock(return_value=False)),
        patch(
            "routers.chat.send_chat_message",
            new=AsyncMock(side_effect=ExternalServiceError("DIFY_CONN_TIMEOUT")),
        ),
    ):
        response = await client.post(
            "/api/chat",
            json={"session_id": "session-1", "message": "テスト"},
        )

    assert response.status_code == 503
    data = response.json()
    assert data["error_code"] == "DIFY_CONN_TIMEOUT"
    assert data["message"] == "現在サービスが混雑しています"
    assert "trace_id" in data


async def test_バリデーションエラーで400と日本語メッセージを返す(client):
    response = await client.post(
        "/api/chat",
        json={"session_id": "session-1", "message": ""},
    )

    assert response.status_code == 400
    data = response.json()
    assert data["error_code"] == "VALIDATION_ERROR"
    assert data["message"] == "入力内容を確認してください"
    assert "trace_id" in data


async def test_予期せぬ例外でunhandled_error_handlerが呼ばれる(client):
    # BaseHTTPMiddlewareとExceptionハンドラの相互作用により
    # テスト環境では例外が再raiseされるが、
    # ハンドラ自体は呼ばれてログが出力されることを確認する

    with (
        patch("routers.chat.is_rate_limited", new=AsyncMock(return_value=False)),
        patch(
            "routers.chat.send_chat_message",
            new=AsyncMock(side_effect=RuntimeError("unexpected")),
        ),
        patch("main._emit_structured_log") as mock_log,
    ):
        with pytest.raises(RuntimeError):
            await client.post(
                "/api/chat",
                json={"session_id": "session-1", "message": "テスト"},
            )

    mock_log.assert_called_once()
    call_kwargs = mock_log.call_args.kwargs
    assert call_kwargs["level"] == "ERROR"
    assert call_kwargs["action"] == "error.unhandled"


async def test_X_Request_IDヘッダがtrace_idに反映される(client):
    with patch("routers.chat.is_rate_limited", new=AsyncMock(return_value=True)):
        response = await client.post(
            "/api/chat",
            json={"session_id": "session-1", "message": "テスト"},
            headers={"X-Request-ID": "test-trace-id-123"},
        )

    assert response.status_code == 429
    assert response.json()["trace_id"] == "test-trace-id-123"
