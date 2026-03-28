"""
Notion API ページ取得モジュール

Notion REST API v1 を呼び出し、指定ページのページ情報とブロック一覧を取得する。
出力スキーマは normalize.py と互換性を持つ。

使用例:
    from fetch import fetch_page

    data = fetch_page("abc123def456", "your-notion-api-key")
    page = data["page"]
    blocks = data["blocks"]
"""

import requests

NOTION_API_BASE = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"


def _headers(api_key: str) -> dict:
    return {
        "Authorization": f"Bearer {api_key}",
        "Notion-Version": NOTION_VERSION,
    }


def fetch_page(page_id: str, api_key: str) -> dict:
    """
    指定ページのページ情報とブロック一覧を取得して返す。

    Args:
        page_id: Notion ページID
        api_key: Notion Integration Token

    Returns:
        {
            "page": { Notion ページオブジェクト },
            "blocks": [ Notion ブロックオブジェクトのリスト ]
        }
    """
    # ページ情報を取得
    page_url = f"{NOTION_API_BASE}/pages/{page_id}"
    resp = requests.get(page_url, headers=_headers(api_key), timeout=30)
    resp.raise_for_status()
    page = resp.json()

    # ブロック一覧をカーソルページネーションで全取得
    blocks: list[dict] = []
    blocks_url = f"{NOTION_API_BASE}/blocks/{page_id}/children"
    params: dict = {"page_size": 100}

    while True:
        resp = requests.get(
            blocks_url,
            headers=_headers(api_key),
            params=params,
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()

        blocks.extend(data.get("results", []))

        if not data.get("has_more", False):
            break
        params["start_cursor"] = data["next_cursor"]

    print(f"  → {len(blocks)} ブロック取得")
    return {"page": page, "blocks": blocks}
