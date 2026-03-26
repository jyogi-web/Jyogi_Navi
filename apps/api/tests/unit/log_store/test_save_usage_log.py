import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from exceptions import RateLimitExceeded
from services.log_store import (
    check_and_save_usage_log,
    get_daily_token_usage,
    save_usage_log,
)


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


# --- check_and_save_usage_log ---


@pytest.fixture
def mock_session_for_check():
    """check_and_save_usage_log 用: execute を2回呼ぶシナリオに対応したモック。"""
    session = AsyncMock()
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    return session


async def test_check_and_save_usage_log_under_limit(mock_session_for_check):
    """上限未満のとき UsageLog が保存されることを確認。"""
    # 1回目: SELECT FOR UPDATE (session行ロック)、2回目: SUM クエリ
    lock_result = MagicMock()
    sum_result = MagicMock()
    sum_result.scalar.return_value = 0
    mock_session_for_check.execute = AsyncMock(side_effect=[lock_result, sum_result])

    with patch("services.log_store.settings") as mock_settings:
        mock_settings.daily_token_limit = 1000
        await check_and_save_usage_log(
            session=mock_session_for_check,
            session_id="sess-1",
            tokens=200,
            trace_id="trace-1",
        )

    mock_session_for_check.add.assert_called_once()
    mock_session_for_check.commit.assert_awaited_once()


async def test_check_and_save_usage_log_at_limit_raises(mock_session_for_check):
    """使用量が上限に達しているとき RateLimitExceeded が送出されることを確認。"""
    lock_result = MagicMock()
    sum_result = MagicMock()
    sum_result.scalar.return_value = 1000
    mock_session_for_check.execute = AsyncMock(side_effect=[lock_result, sum_result])

    with patch("services.log_store.settings") as mock_settings:
        mock_settings.daily_token_limit = 1000
        with pytest.raises(RateLimitExceeded):
            await check_and_save_usage_log(
                session=mock_session_for_check,
                session_id="sess-1",
                tokens=100,
                trace_id="trace-1",
            )

    mock_session_for_check.add.assert_not_called()
    mock_session_for_check.commit.assert_not_awaited()


async def test_check_and_save_usage_log_acquires_lock(mock_session_for_check):
    """SELECT FOR UPDATE が実行される(execute が最低2回呼ばれる)ことを確認。"""
    lock_result = MagicMock()
    sum_result = MagicMock()
    sum_result.scalar.return_value = 0
    mock_session_for_check.execute = AsyncMock(side_effect=[lock_result, sum_result])

    with patch("services.log_store.settings") as mock_settings:
        mock_settings.daily_token_limit = 1000
        await check_and_save_usage_log(
            session=mock_session_for_check,
            session_id="sess-1",
            tokens=100,
            trace_id="trace-1",
        )

    assert mock_session_for_check.execute.await_count == 2
