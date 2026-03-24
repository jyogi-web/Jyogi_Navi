"""
Discord ログ取り込みパイプライン

fetch.py → normalize.py → upload_dify.py を順に実行し、
全チャンネルのログを Dify ナレッジベースに自動アップロードする。

必要な環境変数:
    DISCORD_BOT_TOKEN   : Discord Bot のトークン
    DISCORD_CHANNEL_IDS : カンマ区切りのチャンネルID（例: "111,222,333"）
    DIFY_API_URL        : Dify の URL（例: https://dify.example.com）
    DIFY_API_KEY        : Dify Dataset API キー
    DIFY_DATASET_ID     : 対象ナレッジベースの ID

使用例:
    python run.py
"""

import os
import sys
from datetime import datetime, timedelta, timezone

from fetch import fetch_channel
from normalize import format_for_dify, is_bot_message, is_stamp_only
from upload_dify import upload_document


def _require_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        print(f"ERROR: 環境変数 {name} が設定されていません", file=sys.stderr)
        sys.exit(1)
    return value


def _normalize_messages(messages: list[dict]) -> list[dict]:
    """Bot・スタンプのみのメッセージを除外する。"""
    return [m for m in messages if not is_bot_message(m) and not is_stamp_only(m)]


def main() -> None:
    # 環境変数から設定を読み込む
    discord_token = _require_env("DISCORD_BOT_TOKEN")
    channel_ids_raw = _require_env("DISCORD_CHANNEL_IDS")
    dify_api_url = _require_env("DIFY_API_URL")
    dify_api_key = _require_env("DIFY_API_KEY")
    dify_dataset_id = _require_env("DIFY_DATASET_ID")

    channel_ids = [cid.strip() for cid in channel_ids_raw.split(",") if cid.strip()]
    if not channel_ids:
        print("ERROR: DISCORD_CHANNEL_IDS にチャンネルIDが含まれていません", file=sys.stderr)
        sys.exit(1)

    after_dt = datetime.now(timezone.utc) - timedelta(days=90)
    run_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    print(f"=== Discord ログ取り込み開始 ({run_date}) ===")
    print(f"対象チャンネル数: {len(channel_ids)}")
    print(f"取得期間: {after_dt.date()} 以降\n")

    success_count = 0
    error_channels: list[str] = []

    for channel_id in channel_ids:
        print(f"[{channel_id}] 処理開始")
        try:
            # 1. Discord API からメッセージ取得
            data = fetch_channel(channel_id, discord_token, after_dt)
            channel_name = data["channel"]["name"]

            # 2. 正規化
            filtered = _normalize_messages(data["messages"])
            text = format_for_dify(channel_name, filtered)
            print(f"  正規化後: {len(filtered)} 件")

            if not filtered:
                print(f"  スキップ: メッセージが0件のためアップロードしません")
                continue

            # 3. Dify にアップロード（ドキュメント名: "discord-{チャンネル名}"）
            doc_name = f"discord-{channel_name}"
            upload_document(dify_api_url, dify_api_key, dify_dataset_id, doc_name, text)

            success_count += 1
            print(f"[{channel_id}] 完了\n")

        except Exception as e:
            print(f"[{channel_id}] ERROR: {e}\n", file=sys.stderr)
            error_channels.append(channel_id)

    # サマリー
    print("=== 完了 ===")
    print(f"成功: {success_count} / {len(channel_ids)} チャンネル")
    if error_channels:
        print(f"失敗: {', '.join(error_channels)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
