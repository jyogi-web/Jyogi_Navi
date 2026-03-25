from unittest.mock import AsyncMock, patch

from db.models import FaqEmbedding


def _make_faq(content: str) -> FaqEmbedding:
    faq = FaqEmbedding()
    faq.content = content
    return faq


async def test_FAQ検索で正常に結果を返す(client):
    mock_rows = [_make_faq("入部するには申し込みフォームを提出してください。")]

    with patch(
        "routers.faq.search_faq_by_keyword", new=AsyncMock(return_value=mock_rows)
    ):
        response = await client.get("/api/faq/search", params={"q": "入部"})

    assert response.status_code == 200
    body = response.json()
    assert "results" in body
    assert len(body["results"]) == 1
    assert (
        body["results"][0]["content"]
        == "入部するには申し込みフォームを提出してください。"
    )


async def test_クエリパラメータ未指定で400を返す(client):
    response = await client.get("/api/faq/search")

    assert response.status_code == 400


async def test_空文字のクエリで400を返す(client):
    response = await client.get("/api/faq/search", params={"q": ""})

    assert response.status_code == 400


async def test_検索結果が0件の場合に空のresultsを返す(client):
    with patch("routers.faq.search_faq_by_keyword", new=AsyncMock(return_value=[])):
        response = await client.get(
            "/api/faq/search", params={"q": "存在しないキーワード"}
        )

    assert response.status_code == 200
    body = response.json()
    assert body == {"results": []}
