from unittest.mock import AsyncMock, patch

import pytest

from services.rate_limit import is_rate_limited

pytestmark = pytest.mark.asyncio


@pytest.fixture
def mock_session():
    return AsyncMock()


async def test_not_rate_limited_when_under_limit(mock_session):
    """使用量が上限未満なら False を返すことを確認。"""
    with patch(
        "services.rate_limit.get_daily_token_usage", return_value=9999
    ) as mock_usage:
        with patch("services.rate_limit.settings") as mock_settings:
            mock_settings.daily_token_limit = 10000
            result = await is_rate_limited(mock_session, "sess-1")
    assert result is False
    mock_usage.assert_called_once_with(mock_session, "sess-1")


async def test_rate_limited_when_at_limit(mock_session):
    """使用量が上限以上なら True を返すことを確認。"""
    with patch("services.rate_limit.get_daily_token_usage", return_value=10000):
        with patch("services.rate_limit.settings") as mock_settings:
            mock_settings.daily_token_limit = 10000
            result = await is_rate_limited(mock_session, "sess-2")
    assert result is True


async def test_rate_limited_when_over_limit(mock_session):
    """使用量が上限超過なら True を返すことを確認。"""
    with patch("services.rate_limit.get_daily_token_usage", return_value=15000):
        with patch("services.rate_limit.settings") as mock_settings:
            mock_settings.daily_token_limit = 10000
            result = await is_rate_limited(mock_session, "sess-3")
    assert result is True
