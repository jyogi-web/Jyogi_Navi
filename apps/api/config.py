import json

from pydantic import SecretStr, model_validator
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

    allowed_origins: list[str] = [
        "http://localhost:3000",  # apps/web
        "http://localhost:3001",  # apps/admin
        "http://localhost:3101",  # Dify Web UI
        "http://127.0.0.1:3101",  # Dify Web UI (127.0.0.1)
    ]

    app_env: str = "development"
    daily_token_limit: int = 10000
    dify_timeout_seconds: float = 30.0

    # GCP Secret Manager から注入される JSON 設定 (本番環境)
    # 例: TIDB_CONFIG='{"host":"...","user":"...","password":"..."}'
    tidb_config: str = ""
    supabase_config: str = ""
    dify_config: str = ""
    discord_config: str = ""

    @model_validator(mode="before")
    @classmethod
    def expand_json_configs(cls, values: dict) -> dict:
        if cfg := values.get("tidb_config"):
            data = json.loads(cfg)
            values.setdefault("tidb_host", data.get("host", ""))
            values.setdefault("tidb_user", data.get("user", ""))
            values.setdefault("tidb_password", data.get("password", ""))
            values.setdefault("tidb_database", data.get("database", ""))
            values.setdefault("tidb_ssl_ca", data.get("ssl_ca", ""))

        if cfg := values.get("supabase_config"):
            data = json.loads(cfg)
            values.setdefault("supabase_url", data.get("url", ""))
            values.setdefault("supabase_secret", data.get("secret", ""))

        if cfg := values.get("dify_config"):
            data = json.loads(cfg)
            values.setdefault("dify_api_base_url", data.get("api_base_url", ""))
            values.setdefault("dify_api_key", data.get("api_key", ""))

        if cfg := values.get("discord_config"):
            data = json.loads(cfg)
            values.setdefault("discord_client_id", data.get("client_id", ""))
            values.setdefault("discord_client_secret", data.get("client_secret", ""))
            values.setdefault("discord_guild_id", data.get("guild_id", ""))

        return values


settings = Settings()
