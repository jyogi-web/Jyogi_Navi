from datetime import date

from pydantic import BaseModel


class DailyCount(BaseModel):
    date: date
    count: int


class AdminStatsResponse(BaseModel):
    daily_counts: list[DailyCount]
    total_tokens: int
    good_rate: float
