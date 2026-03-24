import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from services.log_store import get_daily_token_usage, save_usage_log


@pytest.fixture
def mock_session():
    session = AsyncMock()
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    return session


async def test_save_usage_log_adds_and_commits(mock_session):
    """save_usage_log が session.add / commit を呼ぶことを確認。"""
    await save_usage_log(
        session=mock_session,
        session_id="test-session-id",
        tokens=120,
        trace_id="test-trace-id",
        category="general",
    )
    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once()


async def test_save_usage_log_emits_structured_log(mock_session, caplog):
    """save_usage_log が構造化ログを出力することを確認。"""
    import logging

    with caplog.at_level(logging.INFO, logger="services.log_store"):
        await save_usage_log(
            session=mock_session,
            session_id="sess-abc",
            tokens=50,
            trace_id="trace-xyz",
        )

    assert len(caplog.records) == 1
    record = json.loads(caplog.records[0].message)
    assert record["action"] == "chat.request"
    assert record["trace_id"] == "trace-xyz"
    assert record["metadata"]["session_id"] == "sess-abc"
    assert record["metadata"]["tokens"] == 50
    assert record["level"] == "INFO"
    assert record["service"] == "api"


async def test_save_usage_log_no_message_body(mock_session):
    """save_usage_log がメッセージ本文を保存しないことを確認(引数にない)。"""
    with patch("services.log_store.UsageLog") as MockUsageLog:
        mock_instance = MagicMock()
        MockUsageLog.return_value = mock_instance
        await save_usage_log(
            session=mock_session,
            session_id="s",
            tokens=10,
            trace_id="t",
        )
        call_kwargs = MockUsageLog.call_args.kwargs
        assert "message" not in call_kwargs
        assert "content" not in call_kwargs


async def test_get_daily_token_usage_returns_int(mock_session):
    """get_daily_token_usage が当日トークン合計を int で返すことを確認。"""
    mock_result = MagicMock()
    mock_result.scalar.return_value = 300
    mock_session.execute = AsyncMock(return_value=mock_result)

    result = await get_daily_token_usage(mock_session, "sess-1")
    assert result == 300
    assert isinstance(result, int)
