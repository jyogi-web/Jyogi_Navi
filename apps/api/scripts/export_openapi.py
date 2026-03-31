"""OpenAPIスキーマをJSONファイルに出力するスクリプト。

サーバーを起動せずにFastAPIアプリケーションからOpenAPIスキーマを生成する。
"""

import json
import os
import sys
from pathlib import Path

# プロジェクトルート(apps/api)をPythonパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent))

# スキーマ出力のみに使用するため、必須フィールドにダミー値を設定する
os.environ.setdefault("JWT_SECRET", "dummy-for-schema-export")

from main import app

output_path = Path(__file__).parent.parent / "openapi.json"
schema = app.openapi()

with output_path.open("w", encoding="utf-8") as f:
    json.dump(schema, f, ensure_ascii=False, indent=2)

print(f"OpenAPI schema exported to {output_path}")
