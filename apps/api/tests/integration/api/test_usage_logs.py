from unittest.mock import AsyncMock, MagicMock, patch

import pytest


@pytest.fixture
def mock_usage_log():
    """save_usage_log が返すモックUsageLogオブジェクト。"""
    log = MagicMock()
    log.id = "log-id-1"
    log.session_id = "sess-abc"
    log.tokens = 120
    log.category = "general"
    from datetime import datetime

    log.created_at = datetime(2026, 3, 24, 12, 0, 0)
    return log


async def test_create_usage_log_success(client, mock_usage_log):
    """POST /usage-logs が 201 を返し正しいレスポンスを持つことを確認。"""
    with patch(
        "routers.usage_logs.save_usage_log",
        new_callable=AsyncMock,
        return_value=mock_usage_log,
    ):
        response = await client.post(
            "/usage-logs",
            json={"session_id": "sess-abc", "tokens": 120, "category": "general"},
        )
    assert response.status_code == 201
    data = response.json()
    assert data["session_id"] == "sess-abc"
    assert data["tokens"] == 120
    assert data["category"] == "general"


async def test_create_usage_log_without_category(client, mock_usage_log):
    """category なしで POST /usage-logs が 201 を返すことを確認。"""
    mock_usage_log.category = None
    with patch(
        "routers.usage_logs.save_usage_log",
        new_callable=AsyncMock,
        return_value=mock_usage_log,
    ):
        response = await client.post(
            "/usage-logs",
            json={"session_id": "sess-abc", "tokens": 50},
        )
    assert response.status_code == 201


async def test_create_usage_log_missing_required_field(client):
    """必須フィールド欠如で 400 を返すことを確認。"""
    response = await client.post(
        "/usage-logs",
        json={"session_id": "sess-abc"},  # tokens が欠如
    )
    assert response.status_code == 400
    data = response.json()
    assert data["error_code"] == "VALIDATION_ERROR"
