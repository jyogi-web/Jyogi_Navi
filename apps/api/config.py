from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    tidb_host: str = ""
    tidb_port: int = 4000
    tidb_user: str = ""
    tidb_password: str = ""
    tidb_database: str = ""
    tidb_ssl_ca: str = ""

    supabase_url: str = ""
    supabase_secret: str = ""

    dify_api_base_url: str = ""
    dify_api_key: str = ""

    discord_client_id: str = ""
    discord_client_secret: str = ""
    discord_guild_id: str = ""

    app_env: str = "development"
    daily_token_limit: int = 10000

settings = Settings()
