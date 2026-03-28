"""
Dify ナレッジベース アップロードモジュール

Dify Dataset API を呼び出し、テキストをナレッジベースに登録する。
同名ドキュメントが存在する場合は削除してから再作成する（上書き更新）。

使用例:
    from upload_dify import upload_document

    upload_document(
        api_url="https://dify.example.com",
        api_key="your-dify-api-key",
        dataset_id="your-dataset-id",
        name="notion-活動記録",
        text="# 活動記録\n入部について ...",
    )
"""

import requests

# Dify Dataset API
_DOCUMENTS_PATH = "/v1/datasets/{dataset_id}/documents"
_DELETE_PATH = "/v1/datasets/{dataset_id}/documents/{document_id}"


def _headers(api_key: str) -> dict:
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }


def _list_documents(api_url: str, api_key: str, dataset_id: str) -> list[dict]:
    """ナレッジベース内のドキュメント一覧を取得する。"""
    url = api_url.rstrip("/") + _DOCUMENTS_PATH.format(dataset_id=dataset_id)
    docs = []
    page = 1

    while True:
        resp = requests.get(
            url,
            headers=_headers(api_key),
            params={"page": page, "limit": 100},
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        docs.extend(data.get("data", []))
        if not data.get("has_more", False):
            break
        page += 1

    return docs


def _find_document_by_name(
    api_url: str, api_key: str, dataset_id: str, name: str
) -> str | None:
    """同名ドキュメントのIDを返す。存在しなければ None。"""
    docs = _list_documents(api_url, api_key, dataset_id)
    for doc in docs:
        if doc.get("name") == name:
            return doc["id"]
    return None


def _delete_document(
    api_url: str, api_key: str, dataset_id: str, document_id: str
) -> None:
    """指定ドキュメントを削除する。"""
    url = (
        api_url.rstrip("/")
        + _DELETE_PATH.format(dataset_id=dataset_id, document_id=document_id)
    )
    resp = requests.delete(url, headers=_headers(api_key), timeout=30)
    resp.raise_for_status()


def _create_document(
    api_url: str, api_key: str, dataset_id: str, name: str, text: str
) -> str:
    """テキストでドキュメントを新規作成し、ドキュメントIDを返す。"""
    url = api_url.rstrip("/") + _DOCUMENTS_PATH.format(dataset_id=dataset_id)
    payload = {
        "name": name,
        "text": text,
        "indexing_technique": "high_quality",
        "process_rule": {"mode": "automatic"},
    }
    resp = requests.post(url, headers=_headers(api_key), json=payload, timeout=60)
    resp.raise_for_status()
    return resp.json()["document"]["id"]


def upload_document(
    api_url: str,
    api_key: str,
    dataset_id: str,
    name: str,
    text: str,
) -> str:
    """
    ナレッジベースにドキュメントをアップロードする（同名は上書き）。

    Args:
        api_url: Dify の URL（例: https://dify.example.com）
        api_key: Dify Dataset API キー
        dataset_id: 対象ナレッジベースの ID
        name: ドキュメント名（ページ名ベースで一意になるよう呼び出し元が設定）
        text: アップロードするテキスト本文

    Returns:
        作成されたドキュメントの ID
    """
    existing_id = _find_document_by_name(api_url, api_key, dataset_id, name)
    if existing_id:
        print(f"  既存ドキュメントを削除: {name} ({existing_id})")
        _delete_document(api_url, api_key, dataset_id, existing_id)

    doc_id = _create_document(api_url, api_key, dataset_id, name, text)
    print(f"  ドキュメント作成完了: {name} ({doc_id})")
    return doc_id
