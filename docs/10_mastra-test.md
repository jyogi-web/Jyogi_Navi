# 10_mastra_poc_plan

作成日時: 2026年4月1日
最終更新日時: 2026年4月1日
最終更新者: アリス

# 🧪 Mastra-sdk 移行検証（PoC）計画書

---

## 0️⃣ 背景と目的

現在、Jyogi Navi の AI バックエンドとして Dify Cloud を利用しているが、**「プロンプトのコード管理（Git）」「フロントエンドとの完全な型安全（Zod）」「APIインフラの統合」**を目指し、TypeScript 製の AI フレームワーク `Mastra (@mastra/core)` への移行を検討している。
本検証（PoC）では、既存の設計思想（特に RAG と ログ設計）を Mastra で再現・運用可能かを技術的に評価し、本番採用の Go / No-Go を判断する。

---

## 1️⃣ 検証スコープと環境

| 項目 | 内容 | 備考 |
| --- | --- | --- |
| 検証ブランチ | `experiment/mastra-poc` | `main` から派生 |
| 作業ディレクトリ | `apps/web/src/lib/mastra/`<br>`apps/web/src/app/api/` | モノレポのFE側に統合 |
| LLM プロバイダー | gemini (`gemini-flash-2.5`) | 
| ベクトル DB | TiDB Serverless | `faq_embeddings` テーブルを利用 |
| デプロイ先 | Cloudflare Pages | Next.js API Routes 上で動作確認 |

※ 現行の FastAPI (`apps/api/`) と Dify はそのまま残し、並行稼働させて比較できるようにする。

---

## 2️⃣ 検証フェーズとタスク（Step-by-Step）

### Phase 1: 最小構成の疎通（Hello World & 型安全）
Mastra の基礎セットアップと、Zod による型安全なレスポンスの体験を確認する。

- [ ] `apps/web` に `@mastra/core`, `zod` をインストール。
- [ ] `lib/mastra/agents/usako.ts` を作成し、`00_onboarding.md` に記載の「うさこ」のプロンプトを定義。
- [ ] 出力スキーマを定義（`answer`, `category` など）。
- [ ] `app/api/mastra-chat/route.ts` を作成し、フロントエンドからフェッチして JSON が正しく返るかテスト。

### Phase 2: RAG（知識検索）の再現 ⚠️最重要
Dify が自動でやってくれていた「資料を読んで答える」仕組みを、Mastra の Tool として実装できるか検証する。

- [ ] TiDB の `faq_embeddings` テーブルへ接続する関数を作成。
- [ ] ユーザーの質問をベクトル化し、TiDB から類似テキスト（チャンク）を取得するロジックを実装。
- [ ] 上記を Mastra の `createTool` でラップし、うさこエージェントに持たせる。
- [ ] 「入部方法は？」などの質問に対し、TiDB の知識を使って的確に回答できるか精度を確認。

### Phase 3: ログ設計とインフラ制限のクリア
`04_permission-design.md` および `07_infrastructure.md` の要件を満たせるか確認する。

- [ ] API Route 内で、AI の回答生成後に `usage_logs` テーブルへトークン消費量・カテゴリを INSERT する処理を追加（※本文は保存しないルールを順守）。
- [ ] Cloudflare Pages にデプロイし、Edge ランタイム環境で Mastra が正常に動くか（タイムアウトや非対応モジュールのエラーが出ないか）をテスト。

---

## 3️⃣ 評価基準（Exit Criteria）

以下のすべての条件を満たした場合、Mastra への本番移行（Go）と判断する。

| 評価項目 | 必須条件 (Go サイン) |
| --- | --- |
| **開発体験 (DX)** | フロントエンド側で API レスポンスの型（Zod）が効き、開発しやすさが向上したとチームで合意できること。 |
| **RAG 精度** | TiDB からのベクトル検索ツールが動作し、Dify と同等以上の正確さでサークル情報を回答できること。 |
| **インフラ制約** | Cloudflare Pages 上で、タイムアウトや Edge ランタイム特有のエラーを起こさずに完走すること。 |
| **運用要件** | `usage_logs` への非同期書き込みが正常に行われること。 |

---

## 4️⃣ スケジュール・担当アサイン

PoC は長引かせず、**1〜2週間** をタイムボックスとして区切る。

* **実行担当 (アリス)**: Phase 1 〜 Phase 3 までの実装・デプロイ・評価を単独で一気通貫で行う。
* **チームメンバー**: アリスからの検証完了報告（またはDraft PR）を受け、コードレビューおよび本番移行の Go/No-Go 判断に参加する。

> 💡 **撤退ライン (No-Go の場合):**
> もし Cloudflare の Edge 環境と Mastra の相性が決定的に悪い、あるいは TiDB での自前ベクトル検索の実装コストが高すぎる・遅延が許容できない場合は、無理に移行せず、当面は Dify Cloud の運用を継続する。