"""
Notion fetch.py のテスト

requests をモックして fetch_page の動作を検証する。
"""

from unittest.mock import MagicMock, patch

import pytest

from fetch import fetch_page

_SAMPLE_PAGE = {"id": "page-abc", "object": "page", "properties": {}}

_SAMPLE_BLOCK = {"id": "block-001", "type": "paragraph", "object": "block"}


def _mock_response(json_data: dict, status_code: int = 200) -> MagicMock:
    mock = MagicMock()
    mock.status_code = status_code
    mock.json.return_value = json_data
    mock.raise_for_status = MagicMock()
    return mock


class TestFetchPage:
    def test_returns_page_and_blocks(self):
        page_resp = _mock_response(_SAMPLE_PAGE)
        blocks_resp = _mock_response({
            "results": [_SAMPLE_BLOCK],
            "has_more": False,
        })

        with patch("fetch.requests.get", side_effect=[page_resp, blocks_resp]):
            data = fetch_page("page-abc", "test-api-key")

        assert data["page"] == _SAMPLE_PAGE
        assert data["blocks"] == [_SAMPLE_BLOCK]

    def test_pagination_fetches_all_blocks(self):
        page_resp = _mock_response(_SAMPLE_PAGE)
        block_a = {"id": "block-001", "type": "paragraph", "object": "block"}
        block_b = {"id": "block-002", "type": "heading_1", "object": "block"}

        blocks_page1 = _mock_response({
            "results": [block_a],
            "has_more": True,
            "next_cursor": "cursor-xyz",
        })
        blocks_page2 = _mock_response({
            "results": [block_b],
            "has_more": False,
        })

        with patch("fetch.requests.get", side_effect=[page_resp, blocks_page1, blocks_page2]):
            data = fetch_page("page-abc", "test-api-key")

        assert len(data["blocks"]) == 2
        assert data["blocks"][0]["id"] == "block-001"
        assert data["blocks"][1]["id"] == "block-002"

    def test_raises_on_page_api_error(self):
        error_resp = _mock_response({}, status_code=404)
        error_resp.raise_for_status.side_effect = Exception("404 Not Found")

        with patch("fetch.requests.get", return_value=error_resp):
            with pytest.raises(Exception, match="404"):
                fetch_page("invalid-page", "test-api-key")

    def test_raises_on_blocks_api_error(self):
        page_resp = _mock_response(_SAMPLE_PAGE)
        error_resp = _mock_response({}, status_code=500)
        error_resp.raise_for_status.side_effect = Exception("500 Server Error")

        with patch("fetch.requests.get", side_effect=[page_resp, error_resp]):
            with pytest.raises(Exception, match="500"):
                fetch_page("page-abc", "test-api-key")

    def test_empty_blocks_returns_empty_list(self):
        page_resp = _mock_response(_SAMPLE_PAGE)
        blocks_resp = _mock_response({"results": [], "has_more": False})

        with patch("fetch.requests.get", side_effect=[page_resp, blocks_resp]):
            data = fetch_page("page-abc", "test-api-key")

        assert data["blocks"] == []
