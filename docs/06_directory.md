# 06_directory

作成日時: 2026年3月1日 17:36
最終更新日時: 2026年3月1日 17:36
最終更新者: iseebi

# 📁 ディレクトリ構成図

---

# 0️⃣ 設計前提

| 項目 | 内容 |
| --- | --- |
| リポジトリ構成 | Monorepo |
| アーキテクチャ | Layered（P0は薄く、P1で分離強化） |
| デプロイ単位 | Web（静的/SSR） + API（軽量） |
| 言語 | TypeScript |
| MVP方針 | **P0は新入生向けWeb + 軽量API + scripts** |

---

# 1️⃣ 全体構成（Monorepo想定）

```
root/
├── apps/
│   ├── web/                 # 新入生向けチャットUI（P0）
│   ├── api/                 # 軽量API（ログ保存/PII/評価）（P0）
│   └── admin/               # 管理画面（P1）
├── packages/
│   ├── ui/                  # 共有UI（Button等）
│   ├── shared/              # 型定義・共通関数
│   └── config/              # 環境設定・定数
├── scripts/
│   ├── ingest/              # 手動エクスポート整形（P0）
│   └── ops/                 # KPI集計/バックアップ（P0）
├── infra/
│   ├── docker/              # ローカル検証用
│   └── deploy/              # デプロイスクリプト（簡易）
├── docs/
│   ├── 00_design_memo.md
│   ├── 01_features.md
│   ├── 03_screen_flow.md
│   ├── 04_permissions.md
│   ├── 05_db.md
│   ├── 07_infra.md
│   ├── 08_logging.md
│   └── 09_issues.md
└── README.md
```

---

# 2️⃣ apps/web（P0：新入生UI）

```
apps/web/
├── src/
│   ├── pages/ or app/        # ルーティング
│   ├── features/
│   │   ├── chat/             # チャット画面
│   │   ├── consent/          # オプトイン同意
│   │   └── feedback/         # 👍👎
│   ├── components/           # 共通コンポーネント
│   ├── lib/
│   │   ├── api.ts            # APIクライアント
│   │   └── dify.ts           # Dify呼び出し補助（必要なら）
│   └── styles/
└── package.json
```

---

## 3️⃣ apps/api（P0：軽量API）

```
apps/api/
├── src/
│   ├── routes/
│   │   ├── chat.ts           # Difyプロキシ（任意）
│   │   ├── feedback.ts       # 評価保存
│   │   ├── consent.ts        # 同意保存
│   │   └── health.ts
│   ├── services/
│   │   ├── piiMask.ts        # 正規表現マスキング
│   │   ├── logStore.ts       # DBアクセス
│   │   └── kpi.ts            # 集計
│   ├── middleware/
│   │   ├── rateLimit.ts
│   │   └── requestId.ts
│   └── index.ts
└── package.json
```

---

# 4️⃣ scripts/ingest（P0：手動取り込み支援）

```
scripts/ingest/
├── README.md                 # 手順書（週1更新のやり方）
├── discord/
│   ├── export.md             # Discordの書き出し手順
│   └── normalize.ts          # テキスト整形（ノイズ除去）
└── notion/
    ├── export.md
    └── normalize.ts
```

---

# 5️⃣ apps/admin（P1：管理画面）

```
scripts/ingest/
├── README.md                 # 手順書（週1更新のやり方）
├── discord/
│   ├── export.md             # Discordの書き出し手順
│   └── normalize.ts          # テキスト整形（ノイズ除去）
└── notion/
    ├── export.md
    └── normalize.ts
```

---

# 5️⃣ マイクロサービス構成

```
services/
├── auth-service/
├── core-service/
├── notification-service/
└── gateway/
```

---

# 6️⃣ インフラ構成

```
infra/
├── docker/
│   ├── web.Dockerfile
│   ├── api.Dockerfile
│   └── docker-compose.yml
├── env/
│   ├── .env.example
│   ├── .env.dev
│   └── .env.prod
└── ci/
    └── github-actions.yml
```

---

# 7️⃣ ドキュメント構成

```
docs/
├── 00_vision.md
├── 01_feature-list.md
├── 03_screen-flow.md
├── 04_permission-design.md
├── 05_api-spec.md
├── 06_directory.md
├── 07_infra.md
├── 08_logging.md
├── 09_kpi.md
├── 10_rag-design.md
└── 11_cost-estimation.md
```

---

# 8️⃣ テスト構成

```
tests/
├── unit/
│   ├── usecases/
│   └── rateLimit/
├── integration/
│   ├── api/
│   ├── rag/
│   └── db/
├── e2e/
│   └── chat-flow.spec.ts
└── load/
    └── rate-limit-test.ts
```

---

# 9️⃣ ベクトルDB / AI機能がある場合

メンターの「RAG ON/OFFボタン」反映。

```
packages/
├── rag/
│   ├── retriever.ts
│   ├── prompt-builder.ts
│   ├── rag-toggle.ts
│   └── answer-validator.ts
│
├── llm/
│   ├── openai.client.ts
│   ├── qwen.client.ts
│   └── cost-tracker.ts
```

---

## 🔥 RAG切替ロジック

```
if (ragEnabled) {
context=awaitretriever.search(query)
}else {
context=""
}
```

---

# 🔟 状態管理分離パターン（FE）

```
stores/
├── session.store.ts
├── rateLimit.store.ts
├── consent.store.ts
└── rag.store.ts
```

---

# 11️⃣ API設計分離パターン

```
apps/api/src/
├── routes/
│   ├── chat.route.ts
│   ├── feedback.route.ts
│   ├── rag-toggle.route.ts
│   └── stats.route.ts
│
├── usecases/
│   ├── sendMessage.usecase.ts
│   ├── calculateUsage.usecase.ts
│   ├── enforceRateLimit.usecase.ts
│   └── toggleRag.usecase.ts
│
├── infrastructure/
│   ├── db/
│   ├── llm/
│   ├── rag/
│   └── cost/
│
├── middleware/
│   ├── rateLimit.ts
│   ├── tokenLogger.ts
│   └── consentCheck.ts
│
└── domain/
    ├── UsageLog.ts
    ├── Session.ts
    └── RatePolicy.ts
```