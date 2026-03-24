"""フィードバック関連の Pydantic スキーマ。"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class FeedbackCreate(BaseModel):
    """フィードバック作成リクエスト。"""

    session_id: str
    message_id: str = ""
    rating: bool  # True = 👍, False = 👎


class FeedbackResponse(BaseModel):
    """フィードバックレスポンス。"""

    model_config = ConfigDict(from_attributes=True)

    id: str
    session_id: str
    message_id: str
    rating: bool
    created_at: datetime
