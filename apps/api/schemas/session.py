"""セッション・usage_log 関連の Pydantic スキーマ。"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SessionCreate(BaseModel):
    """セッション作成リクエスト。"""

    is_guest: bool = True


class UsageLogCreate(BaseModel):
    """トークン消費ログ作成リクエスト。"""

    session_id: str
    tokens: int = Field(ge=0)
    category: str = ""


class SessionResponse(BaseModel):
    """セッション作成レスポンス。"""

    model_config = ConfigDict(from_attributes=True)

    id: str
    is_guest: bool
    consented: bool
    created_at: datetime


class UsageLogResponse(BaseModel):
    """トークン消費ログレスポンス。"""

    model_config = ConfigDict(from_attributes=True)

    id: str
    session_id: str
    tokens: int
    category: str
    created_at: datetime
