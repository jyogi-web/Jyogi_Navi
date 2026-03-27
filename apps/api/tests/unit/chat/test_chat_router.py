from unittest.mock import AsyncMock, patch

from exceptions import ExternalServiceError
from services.dify_client import DifyResponse


async def test_正常なチャットリクエストで200を返す(client):
    mock_dify = DifyResponse(answer="じょぎは...", tokens_used=120)

    with (
        patch("routers.chat.is_rate_limited", new=AsyncMock(return_value=False)),
        patch("routers.chat.send_chat_message", new=AsyncMock(return_value=mock_dify)),
        patch("routers.chat.check_and_save_usage_log", new=AsyncMock()),
    ):
        response = await client.post(
            "/api/chat",
            json={"session_id": "session-1", "message": "じょぎについて教えて"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["answer"] == "じょぎは..."
    assert data["tokens_used"] == 120


async def test_レート制限超過で429を返す(client):
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


async def test_Difyエラー時に503を返す(client):
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


async def test_メッセージが空の場合は400を返す(client):
    response = await client.post(
        "/api/chat",
        json={"session_id": "session-1", "message": ""},
    )
    assert response.status_code == 400
    data = response.json()
    assert data["error_code"] == "VALIDATION_ERROR"
    assert data["message"] == "入力内容を確認してください"


async def test_session_idが空の場合は400を返す(client):
    response = await client.post(
        "/api/chat",
        json={"session_id": "", "message": "テスト"},
    )
    assert response.status_code == 400
    data = response.json()
    assert data["error_code"] == "VALIDATION_ERROR"


async def test_ログ保存失敗時もチャット応答は返る(client):
    mock_dify = DifyResponse(answer="回答", tokens_used=10)

    with (
        patch("routers.chat.is_rate_limited", new=AsyncMock(return_value=False)),
        patch("routers.chat.send_chat_message", new=AsyncMock(return_value=mock_dify)),
        patch(
            "routers.chat.check_and_save_usage_log",
            new=AsyncMock(side_effect=Exception("DB error")),
        ),
    ):
        response = await client.post(
            "/api/chat",
            json={"session_id": "session-1", "message": "テスト"},
        )

    assert response.status_code == 200
    assert response.json()["answer"] == "回答"
