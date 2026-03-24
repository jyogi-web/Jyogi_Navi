"""セッション・usage_log 関連の Pydantic スキーマ。"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SessionCreate(BaseModel):
    """セッション作成リクエスト。"""

    is_guest: bool = True


class UsageLogCreate(BaseModel):
    """トークン消費ログ作成リクエスト。"""

    session_id: str = Field(min_length=1)
    tokens: int = Field(ge=1)
    category: str | None = None


class UsageLogResponse(BaseModel):
    """トークン消費ログレスポンス。"""

    model_config = ConfigDict(from_attributes=True)

    id: str
    session_id: str
    tokens: int
    category: str | None
    created_at: datetime
