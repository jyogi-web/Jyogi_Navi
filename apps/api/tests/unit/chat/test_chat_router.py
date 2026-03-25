from unittest.mock import AsyncMock, patch

from services.dify_client import DifyResponse


async def test_正常なチャットリクエストで200を返す(client):
    mock_dify = DifyResponse(answer="じょぎは...", tokens_used=120)

    with (
        patch("routers.chat.is_rate_limited", new=AsyncMock(return_value=False)),
        patch("routers.chat.send_chat_message", new=AsyncMock(return_value=mock_dify)),
        patch("routers.chat.save_usage_log", new=AsyncMock()),
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


async def test_Difyエラー時に502を返す(client):
    from fastapi import HTTPException

    with (
        patch("routers.chat.is_rate_limited", new=AsyncMock(return_value=False)),
        patch(
            "routers.chat.send_chat_message",
            new=AsyncMock(side_effect=HTTPException(status_code=502)),
        ),
    ):
        response = await client.post(
            "/api/chat",
            json={"session_id": "session-1", "message": "テスト"},
        )

    assert response.status_code == 502


async def test_メッセージが空の場合は422を返す(client):
    response = await client.post(
        "/api/chat",
        json={"session_id": "session-1", "message": ""},
    )
    assert response.status_code == 422


async def test_session_idが空の場合は422を返す(client):
    response = await client.post(
        "/api/chat",
        json={"session_id": "", "message": "テスト"},
    )
    assert response.status_code == 422
