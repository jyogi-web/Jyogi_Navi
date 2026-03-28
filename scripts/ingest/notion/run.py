"""
Notion ページ取り込みパイプライン

fetch.py → normalize.py → upload_dify.py を順に実行し、
指定ページを Dify ナレッジベースおよび TiDB faq_embeddings に自動アップロードする。

必要な環境変数:
    NOTION_API_KEY  : Notion Integration Token
    NOTION_PAGE_IDS : カンマ区切りのページID（例: "abc123,def456"）
    DIFY_API_URL    : Dify の URL（例: https://dify.example.com）
    DIFY_API_KEY    : Dify Dataset API キー
    DIFY_DATASET_ID : 対象ナレッジベースの ID

使用例:
    python run.py
"""

import os
import sys

from fetch import fetch_page
from normalize import format_for_dify, get_page_title, to_faq_records
from upload_dify import upload_document


def _require_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        print(f"ERROR: 環境変数 {name} が設定されていません", file=sys.stderr)
        sys.exit(1)
    return value


def _tidb_enabled() -> bool:
    """TiDB 接続に必要な環境変数がすべて設定されているか確認する。"""
    required = ["TIDB_HOST", "TIDB_USER", "TIDB_PASSWORD", "TIDB_DATABASE"]
    return all(os.environ.get(k, "").strip() for k in required)


def main() -> None:
    # 環境変数から設定を読み込む
    notion_api_key = _require_env("NOTION_API_KEY")
    page_ids_raw = _require_env("NOTION_PAGE_IDS")
    dify_api_url = _require_env("DIFY_API_BASE_URL")
    dify_api_key = _require_env("DIFY_API_KEY")
    dify_dataset_id = _require_env("DIFY_DATASET_ID")

    page_ids = [pid.strip() for pid in page_ids_raw.split(",") if pid.strip()]
    if not page_ids:
        print("ERROR: NOTION_PAGE_IDS にページIDが含まれていません", file=sys.stderr)
        sys.exit(1)

    print(f"=== Notion ページ取り込み開始 ===")
    print(f"対象ページ数: {len(page_ids)}\n")

    tidb_available = _tidb_enabled()
    if not tidb_available:
        print(
            "WARN: TiDB 環境変数が未設定のため TiDB への保存をスキップします\n",
            file=sys.stderr,
        )

    success_count = 0
    error_pages: list[str] = []

    for page_id in page_ids:
        print(f"[{page_id}] 処理開始")
        try:
            # 1. Notion API からページ情報とブロック取得
            data = fetch_page(page_id, notion_api_key)
            page = data["page"]
            blocks = data["blocks"]
            page_title = get_page_title(page)

            # 2. 正規化して Dify 用テキストを生成
            text = format_for_dify(page, blocks)
            print(f"  タイトル: {page_title}")

            if not blocks:
                print("  スキップ: ブロックが0件のためアップロードしません")
                continue

            # 3. Dify にアップロード（ドキュメント名: "notion-{ページタイトル}"）
            doc_name = f"notion-{page_title}"
            upload_document(dify_api_url, dify_api_key, dify_dataset_id, doc_name, text)

            # 4. TiDB に構造化保存（1ブロック = 1レコード）
            if tidb_available:
                from upload_tidb import upsert_notion_faq
                faq_records = to_faq_records(page_id, page, blocks)
                count = upsert_notion_faq(page_id, faq_records)
                print(f"  TiDB 保存: {count} 件")

            success_count += 1
            print(f"[{page_id}] 完了\n")

        except Exception as e:
            print(f"[{page_id}] ERROR: {e}\n", file=sys.stderr)
            error_pages.append(page_id)

    # サマリー
    print("=== 完了 ===")
    print(f"成功: {success_count} / {len(page_ids)} ページ")
    if error_pages:
        print(f"失敗: {', '.join(error_pages)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
