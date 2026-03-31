"""認証関連の Pydantic スキーマ。"""

from pydantic import BaseModel, ConfigDict

from db.models import UserRole


class UserResponse(BaseModel):
    """管理ユーザー情報レスポンス。"""

    model_config = ConfigDict(from_attributes=True)

    id: str
    discord_user_id: str
    user_name: str
    role: UserRole
