"""
.env ファイルの個別変数を読み取り、GCP Secret Manager 用の
JSON ペイロードを生成するスクリプト。

使用方法:
    uv run python scripts/gen_secret_payloads.py [--env .env]

出力:
    TIDB_CONFIG:
      {"host": "...", "user": "...", "password": "...", ...}

    infra/gcp/terraform.tfvars への追記スニペット
"""

import argparse
import json
import sys
from pathlib import Path

DEFAULT_SSL_CA = "/etc/ssl/certs/ca-certificates.crt"


def load_env(env_path: Path) -> dict[str, str]:
    env: dict[str, str] = {}
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        # クォートを除去
        value = value.strip().strip("\"'")
        env[key.strip()] = value
    return env


def build_payloads(env: dict[str, str]) -> dict[str, str]:
    tidb = {
        "host": env.get("TIDB_HOST", ""),
        "user": env.get("TIDB_USER", ""),
        "password": env.get("TIDB_PASSWORD", ""),
        "database": env.get("TIDB_DATABASE", ""),
        "ssl_ca": env.get("TIDB_SSL_CA", ""),
    }
    supabase = {
        "url": env.get("SUPABASE_URL", ""),
        "secret": env.get("SUPABASE_SECRET", ""),
    }
    dify = {
        "api_base_url": env.get("DIFY_API_BASE_URL", ""),
        "api_key": env.get("DIFY_API_KEY", ""),
    }
    discord = {
        "client_id": env.get("DISCORD_CLIENT_ID", ""),
        "client_secret": env.get("DISCORD_CLIENT_SECRET", ""),
        "guild_id": env.get("DISCORD_GUILD_ID", ""),
    }
    return {
        "TIDB_CONFIG": json.dumps(tidb, ensure_ascii=False),
        "SUPABASE_CONFIG": json.dumps(supabase, ensure_ascii=False),
        "DIFY_CONFIG": json.dumps(dify, ensure_ascii=False),
        "DISCORD_CONFIG": json.dumps(discord, ensure_ascii=False),
        "ALLOWED_ORIGINS": env.get("ALLOWED_ORIGINS", ""),
    }


def build_tfvars(env: dict[str, str]) -> str:
    ssl_ca = env.get("TIDB_SSL_CA", DEFAULT_SSL_CA)
    lines = [
        f'tidb_host             = "{env.get("TIDB_HOST", "")}"',
        f'tidb_user             = "{env.get("TIDB_USER", "")}"',
        f'tidb_password         = "{env.get("TIDB_PASSWORD", "")}"',
        f'tidb_database         = "{env.get("TIDB_DATABASE", "")}"',
        f'tidb_ssl_ca           = "{ssl_ca}"',
        f'supabase_url          = "{env.get("SUPABASE_URL", "")}"',
        f'supabase_secret       = "{env.get("SUPABASE_SECRET", "")}"',
        f'dify_api_base_url     = "{env.get("DIFY_API_BASE_URL", "")}"',
        f'dify_api_key          = "{env.get("DIFY_API_KEY", "")}"',
        f'discord_client_id     = "{env.get("DISCORD_CLIENT_ID", "")}"',
        f'discord_client_secret = "{env.get("DISCORD_CLIENT_SECRET", "")}"',
        f'discord_guild_id      = "{env.get("DISCORD_GUILD_ID", "")}"',
        f'allowed_origins       = "{env.get("ALLOWED_ORIGINS", "")}"',
    ]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate GCP Secret Manager payloads from .env"
    )
    parser.add_argument(
        "--env", default=".env", help=".env ファイルのパス (デフォルト: .env)"
    )
    args = parser.parse_args()

    env_path = Path(args.env)
    if not env_path.exists():
        print(f"Error: {env_path} が見つかりません", file=sys.stderr)
        sys.exit(1)

    env = load_env(env_path)
    payloads = build_payloads(env)

    print("=" * 60)
    print("GCP Secret Manager ペイロード (5 secrets)")
    print("=" * 60)
    for name, value in payloads.items():
        print(f"\n{name}:")
        print(f"  {value}")

    print()
    print("=" * 60)
    print("infra/gcp/terraform.tfvars への追記内容")
    print("(terraform.tfvars に貼り付けてください)")
    print("=" * 60)
    print(build_tfvars(env))


if __name__ == "__main__":
    main()
