"""フィードバック関連の Pydantic スキーマ。"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class FeedbackCreate(BaseModel):
    """フィードバック作成リクエスト。"""

    session_id: str = Field(min_length=1, max_length=128)
    rating: Literal["good", "bad"]
    comment: str | None = Field(default=None, max_length=500)


class FeedbackResponse(BaseModel):
    """フィードバックレスポンス。"""

    model_config = ConfigDict(from_attributes=True)

    id: str
    session_id: str
    rating: str
    comment: str | None
    created_at: datetime
