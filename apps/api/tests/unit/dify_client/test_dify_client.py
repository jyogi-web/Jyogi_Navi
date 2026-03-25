from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from services.dify_client import DifyResponse, send_chat_message


@pytest.fixture
def mock_settings():
    with patch("services.dify_client.settings") as s:
        s.dify_api_base_url = "https://dify.example.com"
        s.dify_api_key = MagicMock()
        s.dify_api_key.get_secret_value.return_value = "test-api-key"
        yield s


async def test_正常応答でDifyResponseを返す(mock_settings):
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = {
        "answer": "じょぎは...",
        "metadata": {"usage": {"total_tokens": 120}},
    }

    with patch("services.dify_client.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client_cls.return_value = mock_client

        result = await send_chat_message("session-1", "じょぎについて教えて")

    assert isinstance(result, DifyResponse)
    assert result.answer == "じょぎは..."
    assert result.tokens_used == 120


async def test_タイムアウト時はExternalServiceError(mock_settings):
    from exceptions import ExternalServiceError

    with patch("services.dify_client.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.post = AsyncMock(side_effect=httpx.TimeoutException("timeout"))
        mock_client_cls.return_value = mock_client

        with pytest.raises(ExternalServiceError) as exc_info:
            await send_chat_message("session-1", "test")

    assert exc_info.value.error_code == "DIFY_CONN_TIMEOUT"
    assert exc_info.value.status_code == 503


async def test_APIエラー時はExternalServiceError(mock_settings):
    from exceptions import ExternalServiceError

    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "error", request=MagicMock(), response=MagicMock()
    )

    with patch("services.dify_client.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client_cls.return_value = mock_client

        with pytest.raises(ExternalServiceError) as exc_info:
            await send_chat_message("session-1", "test")

    assert exc_info.value.error_code == "DIFY_HTTP_ERROR"
    assert exc_info.value.status_code == 503


async def test_接続失敗時はExternalServiceError(mock_settings):
    from exceptions import ExternalServiceError

    with patch("services.dify_client.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.post = AsyncMock(
            side_effect=httpx.RequestError("connection failed")
        )
        mock_client_cls.return_value = mock_client

        with pytest.raises(ExternalServiceError) as exc_info:
            await send_chat_message("session-1", "test")

    assert exc_info.value.error_code == "DIFY_UNREACHABLE"
    assert exc_info.value.status_code == 503


async def test_trace_idがヘッダに付与される(mock_settings):
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = {
        "answer": "回答",
        "metadata": {"usage": {"total_tokens": 10}},
    }

    with patch("services.dify_client.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client_cls.return_value = mock_client

        await send_chat_message("session-1", "test", trace_id="trace-abc")

        _, kwargs = mock_client.post.call_args
        assert kwargs["headers"]["X-Request-ID"] == "trace-abc"


async def test_trace_idが空の場合ヘッダに付与されない(mock_settings):
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = {
        "answer": "回答",
        "metadata": {"usage": {"total_tokens": 10}},
    }

    with patch("services.dify_client.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client_cls.return_value = mock_client

        await send_chat_message("session-1", "test")

        _, kwargs = mock_client.post.call_args
        assert "X-Request-ID" not in kwargs["headers"]


async def test_レスポンスがdictでない場合はExternalServiceError(mock_settings):
    from exceptions import ExternalServiceError

    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = ["unexpected", "list"]

    with patch("services.dify_client.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client_cls.return_value = mock_client

        with pytest.raises(ExternalServiceError) as exc_info:
            await send_chat_message("session-1", "test")

    assert exc_info.value.error_code == "DIFY_INVALID_RESPONSE"
