from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    tidb_host: str = ""
    tidb_port: int = 4000
    tidb_user: str = ""
    tidb_password: SecretStr = SecretStr("")
    tidb_database: str = ""
    tidb_ssl_ca: str = ""

    supabase_url: str = ""
    supabase_secret: SecretStr = SecretStr("")

    dify_api_base_url: str = ""
    dify_api_key: SecretStr = SecretStr("")

    discord_client_id: str = ""
    discord_client_secret: SecretStr = SecretStr("")
    discord_guild_id: str = ""
    discord_redirect_uri: str = "http://localhost:8080/api/auth/callback"

    jwt_secret: SecretStr
    jwt_expire_minutes: int = 60 * 24  # 24時間

    admin_frontend_url: str = "http://localhost:3001"
    jwt_cookie_secure: bool = False  # 本番(HTTPS)環境では True に設定

    allowed_origins: list[str] = [
        "http://localhost:3000",  # apps/web
        "http://localhost:3001",  # apps/admin
        "http://localhost:3101",  # Dify Web UI
        "http://127.0.0.1:3101",  # Dify Web UI (127.0.0.1)
    ]

    app_env: str = "development"
    daily_token_limit: int = 10000
    dify_timeout_seconds: float = 30.0


settings = Settings()
