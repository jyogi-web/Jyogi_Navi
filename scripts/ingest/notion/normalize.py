"""
Notion ページ 正規化スクリプト

Notion API から取得したJSONファイル（ページ情報 + ブロック一覧）を読み込み、
個人情報・ノイズを除去してDify取り込み用のテキストに変換する。

入力JSONフォーマット:
    {
        "page": { Notion ページオブジェクト },
        "blocks": [ Notion ブロックオブジェクトのリスト ]
    }

使用例:
    # 単一ファイル
    python normalize.py --input raw/page.json --output out/page.txt

    # ディレクトリ一括処理
    python normalize.py --input raw/ --output out/
"""

import argparse
import json
import re
import sys
from pathlib import Path

# PII パターン
EMAIL_PATTERN = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")
DISCORD_MENTION_PATTERN = re.compile(r"<@!?\d+>|<#\d+>|<@&\d+>")
URL_PATTERN = re.compile(r"https?://\S+")

# テキストを持つ Notion ブロックタイプ
BLOCK_TEXT_KEYS = {
    "paragraph": "paragraph",
    "heading_1": "heading_1",
    "heading_2": "heading_2",
    "heading_3": "heading_3",
    "bulleted_list_item": "bulleted_list_item",
    "numbered_list_item": "numbered_list_item",
    "to_do": "to_do",
    "toggle": "toggle",
    "quote": "quote",
    "callout": "callout",
    "code": "code",
}

HEADING_PREFIX = {
    "heading_1": "# ",
    "heading_2": "## ",
    "heading_3": "### ",
}


def extract_rich_text(rich_text_list: list[dict]) -> str:
    """rich_text 配列からプレーンテキストを結合して返す。"""
    return "".join(item.get("plain_text", "") for item in rich_text_list)


def get_page_title(page: dict) -> str:
    """ページのタイトルプロパティを取得する。"""
    properties = page.get("properties", {})
    for prop in properties.values():
        if prop.get("type") == "title":
            title = extract_rich_text(prop.get("title", []))
            if title:
                return title
    return "Untitled"


def block_to_text(block: dict) -> str | None:
    """単一ブロックをテキストに変換する。テキストを持たないブロックは None を返す。"""
    block_type = block.get("type", "")
    if block_type not in BLOCK_TEXT_KEYS:
        return None

    block_data = block.get(BLOCK_TEXT_KEYS[block_type], {})
    rich_text = block_data.get("rich_text", [])
    text = extract_rich_text(rich_text)

    if not text.strip():
        return None

    prefix = HEADING_PREFIX.get(block_type, "")
    return f"{prefix}{text}"


def remove_pii(text: str) -> str:
    """Discord メンション・メールアドレスを除去する。"""
    text = DISCORD_MENTION_PATTERN.sub("[mention]", text)
    text = EMAIL_PATTERN.sub("[email]", text)
    return text


def remove_urls(text: str) -> str:
    """URLを除去する。"""
    return URL_PATTERN.sub("", text).strip()


def clean_text(text: str) -> str:
    """PII除去 → URL除去 → 空白整形をまとめて行う。"""
    text = remove_pii(text)
    text = remove_urls(text)
    text = re.sub(r" {2,}", " ", text).strip()
    return text


def format_for_dify(page: dict, blocks: list[dict]) -> str:
    """Dify取り込み用のプレーンテキストを生成する。"""
    title = get_page_title(page)
    lines = [f"# {title}", ""]

    for block in blocks:
        text = block_to_text(block)
        if text is None:
            continue
        cleaned = clean_text(text)
        if cleaned:
            lines.append(cleaned)

    return "\n".join(lines)


def load_page(path: Path) -> tuple[dict, list[dict]]:
    """JSONファイルを読み込み、ページ情報とブロックリストを返す。"""
    with path.open(encoding="utf-8") as f:
        data = json.load(f)

    page = data.get("page", {})
    blocks = data.get("blocks", [])
    return page, blocks


def process_file(input_path: Path, output_path: Path) -> int:
    """単一JSONファイルを処理し、正規化済みテキストを書き出す。

    Returns:
        出力したコンテンツ行数（タイトル行を除く）
    """
    page, blocks = load_page(input_path)
    output_text = format_for_dify(page, blocks)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(output_text, encoding="utf-8")

    # タイトル行・空行（先頭2行）を除いた非空行数を返す
    all_lines = output_text.splitlines()
    content_lines = [line for line in all_lines[2:] if line.strip()]
    return len(content_lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Notion ページを正規化してDify用テキストに変換します。"
    )
    parser.add_argument(
        "--input", "-i", required=True,
        help="入力JSONファイルまたはディレクトリ"
    )
    parser.add_argument(
        "--output", "-o", required=True,
        help="出力先ファイルまたはディレクトリ"
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        print(f"ERROR: 入力パスが存在しません: {input_path}", file=sys.stderr)
        sys.exit(1)

    if input_path.is_file():
        out_file = output_path if output_path.suffix else output_path / (input_path.stem + ".txt")
        count = process_file(input_path, out_file)
        print(f"[OK] {input_path.name} → {out_file.name}  ({count} blocks)")
    elif input_path.is_dir():
        json_files = sorted(input_path.glob("*.json"))
        if not json_files:
            print(f"WARN: JSONファイルが見つかりません: {input_path}", file=sys.stderr)
            sys.exit(0)

        total = 0
        for json_file in json_files:
            out_file = output_path / (json_file.stem + ".txt")
            count = process_file(json_file, out_file)
            total += count
            print(f"[OK] {json_file.name} → {out_file.name}  ({count} blocks)")

        print(f"\n完了: {len(json_files)} ファイル, 合計 {total} ブロック")
    else:
        print(f"ERROR: 入力パスがファイルでもディレクトリでもありません: {input_path}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
