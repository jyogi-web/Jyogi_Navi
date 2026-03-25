"""FAQ検索関連の Pydantic スキーマ。"""

from pydantic import BaseModel


class FaqSearchResult(BaseModel):
    """FAQ検索結果の1件。"""

    content: str


class FaqSearchResponse(BaseModel):
    """FAQ検索レスポンス。"""

    results: list[FaqSearchResult]
