"""認証関連の Pydantic スキーマ。"""

from pydantic import BaseModel, ConfigDict


class UserResponse(BaseModel):
    """管理ユーザー情報レスポンス。"""

    model_config = ConfigDict(from_attributes=True)

    id: str
    discord_user_id: str
    role: str
