from unittest.mock import AsyncMock, patch

from services.dify_client import DifyResponse


async def test_チャットエンドポイントが正常に応答する(client):
    mock_dify = DifyResponse(answer="じょぎは学生自治組織です。", tokens_used=50)

    with (
        patch("routers.chat.is_rate_limited", new=AsyncMock(return_value=False)),
        patch("routers.chat.send_chat_message", new=AsyncMock(return_value=mock_dify)),
        patch("routers.chat.check_and_save_usage_log", new=AsyncMock()),
    ):
        response = await client.post(
            "/api/chat",
            json={"session_id": "integration-session-1", "message": "じょぎとは"},
        )

    assert response.status_code == 200
    body = response.json()
    assert "answer" in body
    assert "tokens_used" in body
    assert body["tokens_used"] == 50


async def test_レート制限超過時に429を返す(client):
    with patch("routers.chat.is_rate_limited", new=AsyncMock(return_value=True)):
        response = await client.post(
            "/api/chat",
            json={"session_id": "limited-session", "message": "テスト"},
        )

    assert response.status_code == 429
    data = response.json()
    assert data["error_code"] == "RATE_LIMIT_EXCEEDED"
    assert data["message"] == "本日の質問上限に達しました"
