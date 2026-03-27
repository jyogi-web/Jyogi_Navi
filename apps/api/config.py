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

    allowed_origins: list[str] = ["http://localhost:3000", "http://localhost:3001"]

    app_env: str = "development"
    daily_token_limit: int = 10000
    dify_timeout_seconds: float = 30.0


settings = Settings()
