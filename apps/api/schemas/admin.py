from datetime import date

from pydantic import BaseModel


class DailyCount(BaseModel):
    day: date
    count: int


class AdminStatsResponse(BaseModel):
    daily_questions: list[DailyCount]
    total_tokens: int
