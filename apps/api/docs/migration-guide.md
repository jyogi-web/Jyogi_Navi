# DBマイグレーション ガイド

APIサーバー (`apps/api`) のデータベースマイグレーションは [Alembic](https://alembic.sqlalchemy.org/) で管理しています。
接続先は TiDB Serverless (MySQL互換) です。

## 前提条件

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) がインストール済み
- `.env` に TiDB 接続情報が設定済み（`.env.example` を参照）

## セットアップ

```bash
cd apps/api
uv sync          # 依存パッケージをインストール
cp .env.example .env
# .env を編集して TiDB の接続情報を記入
```

## よく使うコマンド

すべてのコマンドは `apps/api/` ディレクトリで実行してください。

### マイグレーションを適用する（最新まで）

```bash
uv run alembic upgrade head
```

### 現在のリビジョンを確認する

```bash
uv run alembic current
```

### マイグレーション履歴を確認する

```bash
uv run alembic history
```

### 1つ前のリビジョンに戻す

```bash
uv run alembic downgrade -1
```

### 特定のリビジョンに戻す

```bash
uv run alembic downgrade <revision_id>
```

### すべてのマイグレーションを取り消す

```bash
uv run alembic downgrade base
```

## 新しいマイグレーションを作成する

### 1. ORMモデルを編集する

`apps/api/db/models.py` にテーブル定義を追加・変更します。

```python
# 例: 新しいテーブルを追加
class Feedback(Base):
    __tablename__ = "feedbacks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id: Mapped[str] = mapped_column(String(36), ForeignKey("sessions.id"))
    rating: Mapped[str] = mapped_column(String(10))
    comment: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
```

### 2. マイグレーションファイルを自動生成する

```bash
uv run alembic revision --autogenerate -m "add feedbacks table"
```

`migrations/versions/` に新しいファイルが生成されます。

### 3. 生成されたファイルを確認する

自動生成の内容を確認し、必要に応じて手動で修正してください。
特に以下の点に注意：

- インデックスが正しく定義されているか
- `server_default` が意図通りか
- `downgrade()` でロールバックが正しく動作するか

### 4. マイグレーションを適用する

```bash
uv run alembic upgrade head
```

## アーキテクチャ

```
apps/api/
├── alembic.ini                    # Alembic 設定（接続URLは .env から読み込み）
├── db/
│   ├── models.py                  # SQLAlchemy ORM モデル定義
│   └── session.py                 # 非同期エンジン・セッション管理
└── migrations/
    ├── env.py                     # Alembic 環境設定（非同期対応）
    ├── script.py.mako             # マイグレーションファイルのテンプレート
    └── versions/
        └── 001_create_sessions_and_usage_logs.py  # 初回マイグレーション
```

### 接続URLの解決

`alembic.ini` の `sqlalchemy.url` はプレースホルダーです。
実際の接続URLは `migrations/env.py` 内の `_get_url()` が `.env` の環境変数から構築します。

```
mysql+aiomysql://{TIDB_USER}:{TIDB_PASSWORD}@{TIDB_HOST}:{TIDB_PORT}/{TIDB_DATABASE}
```

### 非同期対応

TiDB への接続は `aiomysql` ドライバーを使った非同期接続です。
`env.py` では `async_engine_from_config` + `asyncio.run()` で Alembic の同期インターフェースと橋渡ししています。

## トラブルシューティング

### `ModuleNotFoundError: No module named 'config'`

`apps/api/` ディレクトリで実行しているか確認してください。
Alembic はプロジェクトルートからではなく `apps/api/` から実行する必要があります。

### `Can't connect to MySQL server`

`.env` の TiDB 接続情報を確認してください。
TiDB Serverless は SSL 接続が必要です。`TIDB_SSL_CA` にCA証明書のパスを設定してください。

### `Target database is not up to date`

未適用のマイグレーションがあります。`uv run alembic upgrade head` で最新に更新してください。
