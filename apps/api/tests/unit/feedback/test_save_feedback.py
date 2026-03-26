import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from services.feedback_store import save_feedback


@pytest.fixture
def mock_session():
    session = AsyncMock()
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    return session


async def test_save_feedback_adds_and_commits(mock_session):
    """save_feedback が session.add / commit / refresh を呼ぶことを確認。"""
    await save_feedback(
        session=mock_session,
        session_id="test-session-id",
        rating="good",
        comment=None,
        trace_id="test-trace-id",
    )
    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once()


async def test_save_feedback_emits_structured_log(mock_session, caplog):
    """save_feedback が構造化ログを出力することを確認。"""
    import logging

    with caplog.at_level(logging.INFO, logger="services.log_store"):
        await save_feedback(
            session=mock_session,
            session_id="sess-abc",
            rating="bad",
            comment="回答が不正確でした",
            trace_id="trace-xyz",
        )

    assert len(caplog.records) == 1
    record = json.loads(caplog.records[0].message)
    assert record["action"] == "feedback.submit"
    assert record["trace_id"] == "trace-xyz"
    assert record["metadata"]["session_id"] == "sess-abc"
    assert record["metadata"]["rating"] == "bad"
    assert record["level"] == "INFO"
    assert record["service"] == "api"


async def test_save_feedback_with_comment(mock_session):
    """save_feedback にコメントを渡した場合も正常に動作することを確認。"""
    with patch("services.feedback_store.Feedback") as MockFeedback:
        mock_instance = MagicMock()
        MockFeedback.return_value = mock_instance
        await save_feedback(
            session=mock_session,
            session_id="s",
            rating="good",
            comment="とても分かりやすかったです",
            trace_id="t",
        )
        call_kwargs = MockFeedback.call_args.kwargs
        assert call_kwargs["comment"] == "とても分かりやすかったです"


async def test_save_feedback_without_comment(mock_session):
    """save_feedback にコメントなしでも正常に動作することを確認。"""
    with patch("services.feedback_store.Feedback") as MockFeedback:
        mock_instance = MagicMock()
        MockFeedback.return_value = mock_instance
        await save_feedback(
            session=mock_session,
            session_id="s",
            rating="good",
            comment=None,
            trace_id="t",
        )
        call_kwargs = MockFeedback.call_args.kwargs
        assert call_kwargs["comment"] is None
