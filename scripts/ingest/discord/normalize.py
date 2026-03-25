"""
Discord ログ 正規化スクリプト

DiscordChatExporter が出力したJSONファイルを読み込み、
個人情報・ノイズを除去してDify取り込み用のテキストに変換する。

使用例:
    # 単一ファイル
    python normalize.py --input raw/channel.json --output out/channel.txt

    # ディレクトリ一括処理
    python normalize.py --input raw/ --output out/
"""

import argparse
import json
import re
import sys
from pathlib import Path

# DiscordChatExporter の JSON スキーマに合わせた定数
EMOJI_ONLY_PATTERN = re.compile(
    r"^[\s"
    r"\U0001F600-\U0001F64F"  # Emoticons
    r"\U0001F300-\U0001F5FF"  # Misc Symbols and Pictographs
    r"\U0001F680-\U0001F6FF"  # Transport and Map
    r"\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
    r"\U0001FA00-\U0001FAFF"  # Symbols and Pictographs Extended-A
    r"\U0001F1E0-\U0001F1FF"  # Flags
    r"\U00002600-\U000026FF"  # Miscellaneous Symbols (☀️ ⭐ ❤️ など)
    r"\U00002702-\U000027BF"  # Dingbats
    r"\U0000FE00-\U0000FE0F"  # Variation Selectors (絵文字修飾子)
    r"]*$"
)
MENTION_PATTERN = re.compile(r"<@!?\d+>|<#\d+>|<@&\d+>")
EMAIL_PATTERN = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")
URL_PATTERN = re.compile(r"https?://\S+")


def load_messages(path: Path) -> tuple[str, list[dict]]:
    """JSONファイルを読み込み、チャンネル名とメッセージリストを返す。"""
    with path.open(encoding="utf-8") as f:
        data = json.load(f)

    channel_name = data.get("channel", {}).get("name", path.stem)
    messages = data.get("messages", [])
    return channel_name, messages


def is_bot_message(msg: dict) -> bool:
    """Botによるメッセージかどうかを判定する。"""
    author = msg.get("author", {})
    return bool(author.get("isBot", False))


def is_stamp_only(msg: dict) -> bool:
    """スタンプのみ・絵文字のみ・空メッセージかどうかを判定する。"""
    content = msg.get("content", "").strip()
    if not content:
        return True
    return bool(EMOJI_ONLY_PATTERN.fullmatch(content))


def remove_pii(text: str) -> str:
    """メンションIDとメールアドレスを除去する。"""
    text = MENTION_PATTERN.sub("[mention]", text)
    text = EMAIL_PATTERN.sub("[email]", text)
    return text


def remove_urls(text: str) -> str:
    """埋め込みURLを除去する。"""
    return URL_PATTERN.sub("", text).strip()


def clean_content(text: str) -> str:
    """PII除去 → URL除去 → 空白整形をまとめて行う。"""
    text = remove_pii(text)
    text = remove_urls(text)
    # 連続する空白を1つに圧縮
    text = re.sub(r" {2,}", " ", text).strip()
    return text


def format_timestamp(timestamp_str: str) -> str:
    """ISO 8601 タイムスタンプを読みやすい形式に変換する。"""
    # "2024-01-15T10:30:00+09:00" → "2024-01-15 10:30"
    try:
        return timestamp_str[:16].replace("T", " ")
    except Exception:
        return timestamp_str


def format_for_dify(channel_name: str, messages: list[dict]) -> str:
    """Dify取り込み用のプレーンテキストを生成する。"""
    lines = [f"# {channel_name}", ""]
    for msg in messages:
        author = msg.get("author", {}).get("name", "unknown")
        timestamp = format_timestamp(msg.get("timestamp", ""))
        content = clean_content(msg.get("content", ""))

        if not content:
            continue

        lines.append(f"{timestamp} {author}: {content}")

    return "\n".join(lines)


def process_file(input_path: Path, output_path: Path) -> int:
    """単一JSONファイルを処理し、正規化済みテキストを書き出す。

    Returns:
        出力したメッセージ数
    """
    channel_name, messages = load_messages(input_path)

    filtered = [
        msg for msg in messages
        if not is_bot_message(msg) and not is_stamp_only(msg)
    ]

    output_text = format_for_dify(channel_name, filtered)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(output_text, encoding="utf-8")

    return len(filtered)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Discord ログを正規化してDify用テキストに変換します。"
    )
    parser.add_argument(
        "--input", "-i", required=True,
        help="入力JSONファイルまたはディレクトリ（raw/ 以下）"
    )
    parser.add_argument(
        "--output", "-o", required=True,
        help="出力先ファイルまたはディレクトリ（out/ 以下）"
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        print(f"ERROR: 入力パスが存在しません: {input_path}", file=sys.stderr)
        sys.exit(1)

    if input_path.is_file():
        # 単一ファイルモード
        out_file = output_path if output_path.suffix else output_path / (input_path.stem + ".txt")
        count = process_file(input_path, out_file)
        print(f"[OK] {input_path.name} → {out_file.name}  ({count} messages)")
    elif input_path.is_dir():
        # ディレクトリ一括モード
        json_files = sorted(input_path.glob("*.json"))
        if not json_files:
            print(f"WARN: JSONファイルが見つかりません: {input_path}", file=sys.stderr)
            sys.exit(0)

        total = 0
        for json_file in json_files:
            out_file = output_path / (json_file.stem + ".txt")
            count = process_file(json_file, out_file)
            total += count
            print(f"[OK] {json_file.name} → {out_file.name}  ({count} messages)")

        print(f"\n完了: {len(json_files)} ファイル, 合計 {total} メッセージ")
    else:
        print(f"ERROR: 入力パスがファイルでもディレクトリでもありません: {input_path}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
