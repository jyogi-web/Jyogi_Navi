"""
Discord API メッセージ取得モジュール

Discord REST API を直接呼び出し、指定チャンネルの直近3ヶ月分のメッセージを取得する。
出力スキーマは normalize.py と互換性を持つ。

使用例:
    from fetch import fetch_channel
    from datetime import datetime, timedelta, timezone

    after_dt = datetime.now(timezone.utc) - timedelta(days=90)
    data = fetch_channel("1215894284428120170", "YOUR_BOT_TOKEN", after_dt)
"""

import time
from datetime import datetime, timedelta, timezone

import requests

DISCORD_API_BASE = "https://discord.com/api/v10"
# Discord API のレート制限: 1チャンネルあたり5req/5sec
REQUEST_INTERVAL = 1.0  # 秒


def _get_headers(token: str) -> dict:
    return {"Authorization": f"Bot {token}"}


def _get_channel_name(channel_id: str, token: str) -> str:
    """チャンネル名を取得する。失敗時は channel_id を返す。"""
    url = f"{DISCORD_API_BASE}/channels/{channel_id}"
    try:
        resp = requests.get(url, headers=_get_headers(token), timeout=10)
        resp.raise_for_status()
        return resp.json().get("name", channel_id)
    except Exception:
        return channel_id


def _snowflake_from_datetime(dt: datetime) -> str:
    """datetime を Discord Snowflake ID（文字列）に変換する。"""
    discord_epoch = 1420070400000  # 2015-01-01 UTC in ms
    ms = int(dt.timestamp() * 1000) - discord_epoch
    snowflake = ms << 22
    return str(snowflake)


def _parse_timestamp(ts: str) -> datetime:
    """Discord のタイムスタンプ文字列を datetime に変換する。"""
    # "2024-01-15T10:00:00+00:00" 形式
    try:
        return datetime.fromisoformat(ts)
    except Exception:
        return datetime.min.replace(tzinfo=timezone.utc)


def fetch_channel(
    channel_id: str,
    token: str,
    after_dt: datetime | None = None,
) -> dict:
    """
    指定チャンネルのメッセージを取得して normalize.py 互換スキーマで返す。

    Args:
        channel_id: Discord チャンネルID
        token: Discord Bot トークン
        after_dt: この日時以降のメッセージのみ取得（デフォルト: 90日前）

    Returns:
        {
            "channel": {"id": ..., "name": ...},
            "messages": [{"id", "timestamp", "author": {"id","name","isBot"}, "content"}, ...]
        }
    """
    if after_dt is None:
        after_dt = datetime.now(timezone.utc) - timedelta(days=90)

    if after_dt.tzinfo is None:
        after_dt = after_dt.replace(tzinfo=timezone.utc)

    channel_name = _get_channel_name(channel_id, token)
    print(f"  チャンネル取得中: #{channel_name} ({channel_id})")

    messages: list[dict] = []
    # 最古のメッセージIDを追跡してページネーション（新→旧の順で取得）
    before_id: str | None = None
    after_snowflake = _snowflake_from_datetime(after_dt)

    url = f"{DISCORD_API_BASE}/channels/{channel_id}/messages"

    while True:
        params: dict = {"limit": 100}
        if before_id:
            params["before"] = before_id

        resp = requests.get(
            url,
            headers=_get_headers(token),
            params=params,
            timeout=10,
        )

        if resp.status_code == 429:
            retry_after = float(resp.json().get("retry_after", 1.0))
            print(f"  レート制限: {retry_after}秒待機")
            time.sleep(retry_after)
            continue

        resp.raise_for_status()
        batch: list[dict] = resp.json()

        if not batch:
            break

        reached_limit = False
        for msg in batch:
            if msg["id"] <= after_snowflake:
                reached_limit = True
                break

            messages.append({
                "id": msg["id"],
                "timestamp": msg.get("timestamp", ""),
                "author": {
                    "id": msg["author"]["id"],
                    "name": msg["author"].get("global_name") or msg["author"].get("username", ""),
                    "isBot": msg["author"].get("bot", False),
                },
                "content": msg.get("content", ""),
            })

        if reached_limit or len(batch) < 100:
            break

        before_id = batch[-1]["id"]
        time.sleep(REQUEST_INTERVAL)

    # 時系列順（古い→新しい）に並び替え
    messages.sort(key=lambda m: m["id"])

    print(f"  → {len(messages)} 件取得")
    return {
        "channel": {"id": channel_id, "name": channel_name},
        "messages": messages,
    }
