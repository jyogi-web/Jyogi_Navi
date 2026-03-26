from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


@pytest.fixture
def mock_feedback():
    """save_feedback が返すモックFeedbackオブジェクト。"""
    feedback = MagicMock()
    feedback.id = "fb-id-1"
    feedback.session_id = "sess-abc"
    feedback.rating = "good"
    feedback.comment = None
    feedback.created_at = datetime(2026, 3, 26, 12, 0, 0)
    return feedback


async def test_正常なフィードバック_goodで201を返す(client, mock_feedback):
    """POST /feedback が 201 を返し正しいレスポンスを持つことを確認 (good)。"""
    with patch(
        "routers.feedback.save_feedback",
        new_callable=AsyncMock,
        return_value=mock_feedback,
    ):
        response = await client.post(
            "/feedback",
            json={"session_id": "sess-abc", "rating": "good"},
        )
    assert response.status_code == 201
    data = response.json()
    assert data["session_id"] == "sess-abc"
    assert data["rating"] == "good"
    assert data["comment"] is None


async def test_正常なフィードバック_badで201を返す(client, mock_feedback):
    """POST /feedback が 201 を返し正しいレスポンスを持つことを確認 (bad)。"""
    mock_feedback.rating = "bad"
    with patch(
        "routers.feedback.save_feedback",
        new_callable=AsyncMock,
        return_value=mock_feedback,
    ):
        response = await client.post(
            "/feedback",
            json={"session_id": "sess-abc", "rating": "bad"},
        )
    assert response.status_code == 201
    data = response.json()
    assert data["rating"] == "bad"


async def test_コメント付きフィードバックで201を返す(client, mock_feedback):
    """コメントありで POST /feedback が 201 を返すことを確認。"""
    mock_feedback.comment = "とても分かりやすかったです"
    with patch(
        "routers.feedback.save_feedback",
        new_callable=AsyncMock,
        return_value=mock_feedback,
    ):
        response = await client.post(
            "/feedback",
            json={
                "session_id": "sess-abc",
                "rating": "good",
                "comment": "とても分かりやすかったです",
            },
        )
    assert response.status_code == 201
    data = response.json()
    assert data["comment"] == "とても分かりやすかったです"


async def test_ratingが不正値で400を返す(client):
    """rating が "good"/"bad" 以外の場合は 400 を返すことを確認。"""
    response = await client.post(
        "/feedback",
        json={"session_id": "sess-abc", "rating": "neutral"},
    )
    assert response.status_code == 400
    data = response.json()
    assert data["error_code"] == "VALIDATION_ERROR"


async def test_session_idが空で400を返す(client):
    """session_id が空の場合は 400 を返すことを確認。"""
    response = await client.post(
        "/feedback",
        json={"session_id": "", "rating": "good"},
    )
    assert response.status_code == 400
    data = response.json()
    assert data["error_code"] == "VALIDATION_ERROR"


async def test_ratingが欠如で400を返す(client):
    """rating が欠如した場合は 400 を返すことを確認。"""
    response = await client.post(
        "/feedback",
        json={"session_id": "sess-abc"},
    )
    assert response.status_code == 400
    data = response.json()
    assert data["error_code"] == "VALIDATION_ERROR"
