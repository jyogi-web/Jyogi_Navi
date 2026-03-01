# 02_tech-stack

作成日時: 2026年3月1日 17:49
最終更新日時: 2026年3月1日 17:50
最終更新者: iseebi

# 技術スタック

---

## 0️⃣ 前提定義（最初に決める）

| 項目 | 内容 | 備考 |
| --- | --- | --- |
| プロダクト種別 | サークル専用SaaS |  |
| 想定ユーザー規模 | MAU：50 / 年度はじめだけ増加 |  |
| 可用性目標 | 99.0% |  |
| セキュリティ要件 | （法令準拠 / 監査対応 / 個人情報レベル）
コミュニティ限定認可 (Discord依存) |  |
| パフォーマンス要件 | LLM応答: 10秒以内 / UI操作: 500ms以内 |  |
| チーム体制 | 4名(フルスタック / 開発兼運用) |  |
| リリース頻度 | 随時 (CI/CDによる継続的デリバリー) |  |
| 予算制約 | 月額上限 0円 (完全無料枠運用) | 自宅PC（Dify）/ Cloud Run（API）/ Cloudflare Pages（FE）/ Supabase / TiDB の無料枠を徹底活用 |
| 既存資産 | Discordログ / Notionナレッジ |  |

---

# 1️⃣ 技術スタック構成

---

## 🖥 フロントエンド

| 項目 | 採用技術 | 採用理由 | 評価観点 | 備考 |
| --- | --- | --- | --- | --- |
| 言語 |  TypeScript | 型安全により、Discordの複雑なAPIレスポンスも安全に扱えるため。 | 型安全性 / 学習コスト / 保守性 |  |
| フレームワーク | Next.js (App Router) | SSR/ISRによる高速化と、API Routesによる軽量なバックエンド処理の完結。
 | エコシステム / SSR可否 / パフォーマンス | OpenNextを使用してCloudflareへの対応 |
| UIライブラリ | shadcn/ui + Tailwind CSS | コピー＆ペーストで導入でき、カスタマイズ性が高く、ライブラリ肥大化を防げる。 | デザイン一貫性 / 開発速度 |  |
| 状態管理 | TanStack Query | RAG（API）からのデータ取得・キャッシュ・ローディング状態管理に最適。 | スケール耐性 / Server State分離 |  |
| フォーム管理 | React Hook Form + Zod | スキーマ定義（Zod）により、入力バリデーションを型安全に実装できる | パフォーマンス / バリデーション |  |
| テスト | Vitest | Jestより高速で、Next.jsとの親和性も高い。 | カバレッジ / 実行速度 |  |
|  |  |  |  |  |

---

## 🧠 バックエンド（API Gateway）　将来的な切り離し

| 項目 | 採用技術 | 採用理由 | 評価観点 | 備考 |
| --- | --- | --- | --- | --- |
| 言語 | Python | RAGエコシステム・Difyとの整合性 | 生産性 / 型安全 / 採用市場 | Pydanitcで型安全性 |
| 実行環境 | CloudRun Docker |  | 成熟度 / エコシステム |  |
| フレームワーク | FastAPI | 高速・自動ドキュメント生成 | 構造化 / 拡張性 |  |
| API方式 | REST | 将来別のクライアントが出てきても叩きやすい | 型安全 / 柔軟性 / 過不足 |  |
| ORM / DBアクセス | Supabase-py |  | 型統合 / マイグレーション管理 |  |
| 認証 | Auth.js + Discord |  | セキュリティ / OAuth対応 |  |
| 非同期処理 | Cloud Tasks |  | 再試行 / 耐障害性 |  |

## 🧠 RAG

| 項目 | 採用技術 | 採用理由 | 評価観点 | 備考 |
| --- | --- | --- | --- | --- |
| オーケストレーション | Dify | RAGのパイプライン（分割・埋め込み・検索）をGUIで完結でき、API公開も容易。 | 開発効率 / 運用性 | セルフホスト版 |
| 言語 | Python | Dify自体のコア言語。カスタムツール（プラグイン）開発時に必要。 | エコシステム / 拡張性 |  |
| 実行環境 | Docker |  | 成熟度 / エコシステム |  |
| 内部DB | Supabase (Posgres) | Difyのメタデータ管理 無料のSupabase | コスト / 運用 | MySQLだと度々エラーが出る事例あり |
| ベクトル検索 (Vector) | TiDB Serverless | Difyが標準対応。無料枠が非常に大きく、全文検索とのハイブリッドも得意。 | 検索精度 / スケール性 |  |
| API方式 | Dify Chat API | Streaming（逐次回答）対応。フロントエンド（Next.js）から直接・間接に呼べる。 | 型安全 / 柔軟性 / 過不足 |  |
| Embedding モデル | OpenAI / Gemini | 日本語のセマンティック検索において高精度。 | 検索精度 | 無料枠や少額課金で対応 |
| 認証 |  |  | セキュリティ / OAuth対応 |  |
| 非同期処理 |  |  | 再試行 / 耐障害性 |  |

---

## 🗄 データベース

| 項目 | 採用技術 | 採用理由 | 評価観点 | 備考 |
| --- | --- | --- | --- | --- |
| メインDB | Supabase (PostgreSQL) | Difyの内部DBとしてPostgreSQLが推奨されていて、無料で収まるもの | ACID / スケール性 | 無料枠で500MBまで |
| キャッシュ | Upstash (Redis) | Difyの動作（タスク管理やセッション）を高速化するために必要。 | レイテンシ改善 | 1日1万リクエストまで無料 |
| ベクトル検索 | TiDB Serverless | **12GBまで無料**という圧倒的枠。ベクトル検索と全文検索（ハイブリッド）に強い。 | 全文検索性能 |  |
|  |  |  |  |  |

---

## ☁ インフラ / DevOps

| 項目 | 採用技術 | 採用理由 | 評価観点 | 備考 |
| --- | --- | --- | --- | --- |
| Difyホスティング | 自宅PC（Docker） | docker-composeをそのまま使えて最もシンプル。コスト0円。 | コスト / 運用シンプルさ | Cloudflare Tunnelで公開 |
| APIホスティング | Google Cloud Run | Scale to Zero対応。単一コンテナで動くFastAPIと相性が良い。無料枠で収まる。 | 可用性 / コスト | 月200万リクエストまで無料 |
| フロントエンドホスティング | Cloudflare Pages | CDN・高速。Next.js（OpenNext）に対応。 | パフォーマンス / コスト |  |
| 外部公開 | Cloudflare Tunnel | 自宅PCをポート開放なし・固定IPなしでHTTPS公開できる。 | セキュリティ / 可用性 | cloudflaredをPC常駐 |
| コンテナ | Docker | Dify公式がdocker-compose提供。FastAPIのデプロイにも使用。 | 再現性 / 可搬性 |  |
| CI/CD（FE・API） | GitHub Actions (cloud-hosted) | Cloudflare PagesとCloud Runへの自動デプロイ | 自動化 / 安定性 | lint / test / build / deploy |
| CI/CD（Dify） | GitHub Actions (self-hosted runner) | 自宅PC上でdocker-compose pull & upを自動実行 | 自動化 | 自宅PCにrunnerを常駐 |
| 監視 | Sentry |  | 可観測性 / アラート精度 |  |
| ログ管理 | Cloud Logging | Cloud Run（FastAPI）のログをGoogle Cloud標準機能で管理 | トレーサビリティ |  |
| CDN | Cloudflare | Cloudflare Pages標準付属。DDoS防御も含む。 | レイテンシ最適化 |  |

---

## 🔐 セキュリティ

| 項目 | 方針 | 評価観点 |
| --- | --- | --- |
| 認証方式 | Discord OAuth2 | 標準準拠 / 拡張性 |
| 認可 | Server ID Filter | RBAC / ABAC可否 |
| 通信 | HTTPS  | TLS強制 / 証明書管理 |
| データ保護 | Supabase RLS | 暗号化 / マスキング |
| 脆弱性対策 |  | 自動検査 / パッチ管理 |