import sys
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import ASGITransport, AsyncClient

# db.session モジュールをモックに差し替え(import main より前に実行する必要がある)
_mock_db_module = MagicMock()
_mock_session = AsyncMock()
_mock_session.execute = AsyncMock(return_value=MagicMock())


async def _mock_get_db_session():
    yield _mock_session


_mock_db_module.get_db_session = _mock_get_db_session
sys.modules["db.session"] = _mock_db_module


@pytest.fixture(autouse=True)
def mock_db_session():
    """各テストで参照できるモックセッション。テスト後に side_effect をリセット。"""
    _mock_session.execute.side_effect = None
    _mock_session.execute.return_value = MagicMock()
    yield _mock_session
    _mock_session.execute.side_effect = None


@pytest.fixture
def app(mock_db_session):
    """モック済み db.session を使う FastAPI アプリ。"""
    from main import app as _app

    yield _app


@pytest.fixture
async def client(app):
    """テスト用の非同期 HTTP クライアント。"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as ac:
        yield ac
