# 06_directory

作成日時: 2026年3月1日 17:36
最終更新日時: 2026年3月15日
最終更新者: KOU050223

# 📁 ディレクトリ構成図

---

# 0️⃣ 設計前提

| 項目 | 内容 |
| --- | --- |
| リポジトリ構成 | Monorepo |
| アーキテクチャ | Layered（P0は薄く、P1で分離強化） |
| デプロイ単位 | Web（Cloudflare Workers） + API（Cloud Run） + Dify（自宅PC） |
| 言語 | FE: TypeScript / API: Python |
| MVP方針 | **P0は新入生向けWeb + 軽量API + Dify + scripts** |

---

# 1️⃣ 全体構成（Monorepo想定）

```
root/
├── .github/
│   └── workflows/           # GitHub Actions
├── apps/
│   ├── web/                 # 新入生向けチャットUI（P0）
│   ├── api/                 # 軽量API（ログ保存/PII/評価）（P0）
│   └── admin/               # 管理画面（P1）
├── scripts/
│   ├── ingest/              # 手動エクスポート整形（P0）
│   └── ops/                 # KPI集計/バックアップ（P0）
├── infra/
│   ├── cloudflare/          # Terraform: Cloudflare 周辺リソース（GitHub Secrets 等）
│   ├── dify/                # Dify起動設定（docker-compose）
│   ├── docker/              # API用Dockerfile
│   └── env/                 # 環境変数テンプレート
├── docs/
└── README.md
```

---

# 2️⃣ apps/web（P0：新入生UI）

```
apps/web/
├── src/
│   ├── app/                  # Next.js App Router
│   ├── features/
│   │   ├── chat/             # チャット画面
│   │   ├── consent/          # オプトイン同意
│   │   └── feedback/         # 👍👎
│   ├── components/           # 共通コンポーネント
│   └── lib/
│       ├── api.ts            # Backend APIクライアント
│       └── dify.ts           # Dify Chat API呼び出し
├── vitest.config.ts          # Vitest 設定
├── vitest.setup.ts           # テストセットアップ（jest-dom等）
├── package.json
└── next.config.ts
```

---

# 3️⃣ apps/api（P0：軽量API・Python）

```
apps/api/
├── main.py                   # FastAPI エントリーポイント
├── config.py                 # 設定・環境変数読み込み
├── routers/
│   ├── __init__.py
│   ├── feedback.py           # 評価保存
│   ├── consent.py            # 同意保存
│   └── health.py
├── services/
│   ├── __init__.py
│   ├── pii_mask.py           # 正規表現マスキング
│   ├── log_store.py          # TiDB アクセス
│   └── rate_limit.py         # レート制御ロジック
├── middleware/
│   ├── __init__.py
│   └── request_id.py
├── models/                   # Pydantic スキーマ定義
│   ├── __init__.py
│   ├── feedback.py
│   └── session.py
├── tests/
│   ├── conftest.py           # fixture（db.session モック等）
│   ├── unit/
│   │   ├── pii_mask/         # PII マスク単体テスト
│   │   └── rate_limit/       # レートリミット単体テスト
│   └── integration/
│       ├── api/              # エンドポイント統合テスト
│       └── db/               # DB アクセス統合テスト
├── Dockerfile
├── pyproject.toml            # uv パッケージ管理
├── uv.lock                   # uv ロックファイル
├── requirements.txt
├── .env.example              # 環境変数テンプレート
└── .python-version           # Python バージョン指定
```

---

# 4️⃣ infra/dify（P0：Dify起動設定）

```
infra/dify/
├── docker-compose.yml        # Dify公式composeをベースにカスタマイズ
└── .env.example              # Dify環境変数テンプレート
                              # （TiDB / Supabase / Gemini キー等）
```

> Dify自体のコードは管理しない。公式Dockerイメージをそのまま使用。
> GUIでRAGパイプライン・LLM設定・Chat API公開を管理する。

---

# 5️⃣ scripts/ingest（P0：手動取り込み支援）

```
scripts/ingest/
├── README.md                 # 手順書（週1更新のやり方）
├── discord/
│   ├── export.md             # Discordの書き出し手順
│   └── normalize.py          # テキスト整形（ノイズ除去）
└── notion/
    ├── export.md
    └── normalize.py
```

---

# 6️⃣ apps/admin（P1：管理画面）

```
apps/admin/
├── src/
│   ├── app/                  # Next.js App Router
│   ├── features/
│   │   ├── dashboard/        # KPIダッシュボード
│   │   ├── conversations/    # 会話ログ閲覧
│   │   ├── feedbacks/        # 👍👎評価閲覧
│   │   ├── ingestion/        # 取り込みジョブ管理
│   │   ├── faq/              # FAQ編集
│   │   └── settings/         # システム設定（レート制限等）
│   ├── components/           # 共通コンポーネント
│   └── lib/
│       ├── api.ts            # Backend APIクライアント
│       └── auth.ts           # Discord OAuth連携
├── package.json
└── next.config.ts
```

---

# 7️⃣ infra構成

```
.github/
└── workflows/
    ├── deploy-fe.yml             # Cloudflare Workers へ FEデプロイ（Wrangler）
    ├── deploy-api.yml            # Cloud Run へ FastAPIデプロイ
    └── deploy-dify.yml           # self-hosted runner で Dify再起動

infra/
├── cloudflare/                   # Terraform: Cloudflare 周辺リソース
│   ├── main.tf                   # GitHub Actions Secrets 等のリソース定義
│   ├── variables.tf
│   ├── outputs.tf
│   └── versions.tf               # Provider バージョン固定
├── dify/
│   ├── docker-compose.yml        # Dify公式compose（自宅PC上で実行）
│   └── SETUP.md                  # セットアップ手順
├── docker/
│   └── api.Dockerfile            # FastAPI用（Cloud Run へデプロイ）
└── env/
    ├── .env.example
    ├── .env.dev
    └── .env.prod
```

### CDフロー

```
git push (main)
├── deploy-fe.yml    (cloud-hosted runner)
│   └── Cloudflare Workers へ自動デプロイ（Wrangler）
│
├── deploy-api.yml   (cloud-hosted runner)
│   └── Cloud Run へ FastAPI自動デプロイ
│
└── deploy-dify.yml  (self-hosted runner = 自宅PC)
    └── docker-compose pull && docker-compose up -d
```

---

# 8️⃣ テスト構成

## FE（apps/web）

- フレームワーク: Vitest + Testing Library
- 配置: **コロケーション**（テスト対象ファイルと同じディレクトリに `*.test.tsx` / `*.spec.tsx` を置く）

```
apps/web/src/
├── features/
│   ├── chat/
│   │   ├── ChatContainer.tsx
│   │   └── ChatContainer.test.tsx   # コロケーション
│   └── consent/
│       ├── ConsentScreen.tsx
│       └── ConsentScreen.test.tsx
└── lib/
    ├── api.ts
    └── api.test.ts
```

## BE（apps/api）

- フレームワーク: pytest + pytest-asyncio
- 配置: `apps/api/tests/` 配下に unit / integration で分類

```
apps/api/tests/
├── conftest.py               # fixture（db.session モック等）
├── unit/
│   ├── pii_mask/             # PII マスク単体テスト
│   └── rate_limit/           # レートリミット単体テスト
└── integration/
    ├── api/                  # エンドポイント統合テスト
    └── db/                   # DB アクセス統合テスト
```
