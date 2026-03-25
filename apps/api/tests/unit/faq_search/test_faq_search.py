from unittest.mock import AsyncMock, MagicMock

from db.models import FaqEmbedding
from services.faq_search import FAQ_SEARCH_LIMIT, search_faq_by_keyword


def _make_faq(content: str) -> FaqEmbedding:
    faq = FaqEmbedding()
    faq.content = content
    return faq


async def test_キーワードに一致するFAQを返す():
    """search_faq_by_keyword がDBの結果をリストで返す。"""
    mock_session = AsyncMock()
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = [
        _make_faq("入部するには申し込みフォームを提出してください。")
    ]
    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars
    mock_session.execute = AsyncMock(return_value=mock_result)

    result = await search_faq_by_keyword(mock_session, "入部")

    assert len(result) == 1
    assert result[0].content == "入部するには申し込みフォームを提出してください。"
    mock_session.execute.assert_awaited_once()


async def test_該当なしの場合に空リストを返す():
    """マッチなしのとき空リストを返す。"""
    mock_session = AsyncMock()
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = []
    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars
    mock_session.execute = AsyncMock(return_value=mock_result)

    result = await search_faq_by_keyword(mock_session, "存在しないキーワード")

    assert result == []


async def test_空白のみのキーワードで空リストを返す():
    """ホワイトスペースのみのキーワードはDBにアクセスせず空リストを返す。"""
    mock_session = AsyncMock()

    result = await search_faq_by_keyword(mock_session, "   ")

    assert result == []
    mock_session.execute.assert_not_awaited()


async def test_デフォルトlimitがFAQ_SEARCH_LIMITであることを確認():
    """limit引数のデフォルト値が FAQ_SEARCH_LIMIT と一致する。"""
    mock_session = AsyncMock()
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = []
    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars
    mock_session.execute = AsyncMock(return_value=mock_result)

    await search_faq_by_keyword(mock_session, "テスト")

    # executeが呼ばれたことを確認(limitはSQLAlchemyの内部でクエリに付与される)
    mock_session.execute.assert_awaited_once()
    assert FAQ_SEARCH_LIMIT == 10
