"""
.env ファイルの個別変数を読み取り、GCP Secret Manager 用の
JSON ペイロードを生成するスクリプト。

使用方法:
    # 標準出力に表示するだけ
    uv run python scripts/gen_secret_payloads.py [--env .env]

    # infra/gcp/terraform.tfvars を直接生成
    uv run python scripts/gen_secret_payloads.py --write-tfvars

    # .env と出力先を明示
    uv run python scripts/gen_secret_payloads.py --env .env.local --write-tfvars
"""

import argparse
import json
import sys
from pathlib import Path

# リポジトリルートからの相対パス
TFVARS_PATH = Path(__file__).parents[3] / "infra" / "gcp" / "terraform.tfvars"
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


def build_tfvars_content(env: dict[str, str]) -> str:
    ssl_ca = env.get("TIDB_SSL_CA", DEFAULT_SSL_CA)
    lines = [
        "# このファイルをコピーして terraform.tfvars を作成してください",
        "# terraform.tfvars は .gitignore 済みのため Git にはコミットされません",
        "#",
        "# cp terraform.tfvars.example terraform.tfvars",
        "",
        'gcp_project_id = "<your-gcp-project-id>"  # 手動で設定してください',
        '# gcp_region = "asia-northeast1"  # デフォルト値のまま変更不要な場合はコメントのまま',  # noqa: E501
        "",
        "# GitHub リポジトリ情報 (GitHub Actions OIDC 連携に使用)",
        '# github_owner = "jyogi-web"   # デフォルト値',
        '# github_repo  = "Jyogi_Navi"  # デフォルト値',
        "",
        "# TiDB Serverless",
        f'tidb_host     = "{env.get("TIDB_HOST", "")}"',
        f'tidb_user     = "{env.get("TIDB_USER", "")}"',
        f'tidb_password = "{env.get("TIDB_PASSWORD", "")}"',
        f'tidb_database = "{env.get("TIDB_DATABASE", "")}"',
        f'# tidb_ssl_ca = "{ssl_ca}"  # Cloud Run (Linux) のデフォルト',
        "",
        "# Supabase",
        f'supabase_url    = "{env.get("SUPABASE_URL", "")}"',
        f'supabase_secret = "{env.get("SUPABASE_SECRET", "")}"',
        "",
        "# Dify Chat API",
        f'dify_api_base_url = "{env.get("DIFY_API_BASE_URL", "")}"',
        f'dify_api_key      = "{env.get("DIFY_API_KEY", "")}"',
        "",
        "# Discord OAuth (P1: 管理画面認証)",
        f'discord_client_id     = "{env.get("DISCORD_CLIENT_ID", "")}"',
        f'discord_client_secret = "{env.get("DISCORD_CLIENT_SECRET", "")}"',
        f'discord_guild_id      = "{env.get("DISCORD_GUILD_ID", "")}"',
        "",
        "# CORS 許可オリジン (カンマ区切り)",
        "# 本番デプロイ後に Cloudflare Workers の URL が確定したら更新する",
        f'allowed_origins = "{env.get("ALLOWED_ORIGINS", "")}"',
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate GCP Secret Manager payloads from .env"
    )
    parser.add_argument(
        "--env", default=".env", help=".env ファイルのパス (デフォルト: .env)"
    )
    parser.add_argument(
        "--write-tfvars",
        action="store_true",
        help=f"infra/gcp/terraform.tfvars を直接生成する (出力先: {TFVARS_PATH})",
    )
    args = parser.parse_args()

    env_path = Path(args.env)
    if not env_path.exists():
        print(f"Error: {env_path} が見つかりません", file=sys.stderr)
        sys.exit(1)

    env = load_env(env_path)
    payloads = build_payloads(env)

    # --- Secret Manager ペイロードの表示 ---
    print("=" * 60)
    print("GCP Secret Manager ペイロード (5 secrets)")
    print("=" * 60)
    for name, value in payloads.items():
        print(f"\n{name}:")
        print(f"  {value}")

    # --- terraform.tfvars の生成 ---
    tfvars_content = build_tfvars_content(env)

    if args.write_tfvars:
        TFVARS_PATH.write_text(tfvars_content, encoding="utf-8")
        print(f"\n\u2705 terraform.tfvars を生成しました: {TFVARS_PATH}")
        print("gcp_project_id は手動で設定してください。")
    else:
        print()
        print("=" * 60)
        print("infra/gcp/terraform.tfvars の内容")
        print("(--write-tfvars で直接生成することもできます)")
        print("=" * 60)
        print(tfvars_content)


if __name__ == "__main__":
    main()
