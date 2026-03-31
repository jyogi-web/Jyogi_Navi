from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


class DailyCount(BaseModel):
    date: date
    count: int


class AdminStatsResponse(BaseModel):
    daily_counts: list[DailyCount]
    total_tokens: int
    good_rate: float


class FeedbackItem(BaseModel):
    """フィードバック一覧の1件。"""

    model_config = ConfigDict(from_attributes=True)

    id: str
    session_id: str
    rating: Literal["good", "bad"]
    comment: str | None
    created_at: datetime


class FeedbackListResponse(BaseModel):
    """フィードバック一覧レスポンス。"""

    feedbacks: list[FeedbackItem]
    total: int
