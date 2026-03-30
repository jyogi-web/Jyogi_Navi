# 00_onboarding

作成日時: 2026-03-30
最終更新者: KOU050223

# 🚀 Jyogi Navi オンボーディングガイド

このドキュメントを読めば、開発環境の構築からPRを出すまでの流れがすべてわかります。

---

## 0️⃣ プロジェクト概要

**Jyogi Navi** は、サークル「じょぎ」の新入生向け Q&A チャットボットです。

| 項目 | 内容 |
|---|---|
| 対象ユーザー | じょぎへの入部を検討している新入生 |
| 提供価値 | 気軽に・何度でも・遠慮なくじょぎについて質問できる環境 |
| チーム規模 | 4名（フルスタック・開発兼運用） |
| 予算制約 | 完全無料枠運用（Cloud Run / Cloudflare Pages / TiDB / Supabase の無料枠） |

### システム構成（簡略）

```
新入生ブラウザ
  └─ apps/web（Cloudflare Pages）
       └─ apps/api（Cloud Run / FastAPI）
            └─ Dify（自宅PC / RAG + LLM）
                 └─ TiDB Serverless（ベクトルDB）
```

詳細は [`docs/02_tech-stack.md`](02_tech-stack.md) を参照。

---

## 1️⃣ 事前準備

### 必要アカウント

以下を事前に用意してください。チームメンバーに依頼して招待してもらいます。

- [ ] GitHub（リポジトリへの招待）
- [ ] Discord（じょぎサーバーへの参加 → 管理画面ログインに必要）
- [ ] Google Cloud（Cloud Run デプロイ権限）
- [ ] Cloudflare（Pages デプロイ権限）

---

## 2️⃣ 開発環境セットアップ

このプロジェクトは **Nix + direnv** で開発環境を統一しています。
`pnpm`・`uv`・`terraform`・`tflint` など必要なツールがすべて自動でセットアップされます。

### ステップ 1: Nix をインストール

```bash
curl --proto '=https' --tlsv1.2 -sSf -L https://install.determinate.systems/nix | sh -s -- install
```

インストール後、新しいターミナルを開く。

### ステップ 2: direnv をインストール

```bash
nix profile add nixpkgs#direnv
```

シェルに hook を追加：

```bash
# Zsh の場合
echo 'eval "$(direnv hook zsh)"' >> ~/.zshrc && source ~/.zshrc

# Bash の場合
echo 'eval "$(direnv hook bash)"' >> ~/.bashrc && source ~/.bashrc
```

### ステップ 3: リポジトリをクローン・環境を有効化

```bash
git clone https://github.com/jyogi-web/Jyogi_Navi.git
cd Jyogi_Navi

# .envrc を許可（初回のみ）
direnv allow
```

初回は依存パッケージのダウンロードで数分かかります。完了すると以下のメッセージが出ます：

```
🚀 Jyogi Navi development environment loaded!
  - Node.js v20.x.x
  - pnpm x.x.x
  - Python 3.13.x
  ...
```

> **Nix を使わない場合**: 手動で Node.js 20・Python 3.13・pnpm・uv をインストールしても動きますが、バージョン管理は各自で行ってください。

詳細は [`docs/nix-setup.md`](nix-setup.md) を参照。

### ステップ 4: 依存パッケージをインストール

```bash
# Node.js パッケージ（フロントエンド全体）
pnpm install

# Python パッケージ（バックエンド）
cd apps/api && uv sync --dev && cd ../..
```

### ステップ 5: 環境変数を設定

各アプリケーションディレクトリ（api, web, admin）で `.env` ファイルを作成します。

まず、各ディレクトリの `.env.example` をコピーしてください：

```bash
cp apps/api/.env.example apps/api/.env
cp apps/web/.env.example apps/web/.env
cp apps/admin/.env.example apps/admin/.env
```

その後、`.env` を開いて、チームメンバーから共有された値や必要な値を設定してください。

（例：apps/api の場合）

| 変数 | 用途 | 取得先 |
|---|---|---|
| `TIDB_HOST` 等 | TiDB Serverless 接続情報 | チームメンバーに確認 |
| `DISCORD_CLIENT_ID` 等 | Discord OAuth | Discord Developer Portal |
| `JWT_SECRET` | JWT署名 | 任意のランダム文字列（ローカル用） |
| `DIFY_API_KEY` | Dify Chat API | チームメンバーに確認 |

---

## 3️⃣ ローカルでの起動方法

### バックエンド（apps/api）

```bash
# ルートディレクトリから
pnpm run dev:api
```

または従来通り、
```bash
cd apps/api
uv run uvicorn main:app --reload --port 8080
```

→ http://localhost:8080/docs で Swagger UI が確認できます。

### フロントエンド・新入生向け（apps/web）

```bash
# ルートディレクトリから
pnpm run dev:web
```

または従来通り、
```bash
pnpm --filter web dev
```

→ http://localhost:3000

### フロントエンド・管理画面（apps/admin）

```bash
# ルートディレクトリから
pnpm run dev:admin
```

または従来通り、
```bash
pnpm --filter admin dev
```

→ http://localhost:3001

管理画面のログインには Discord OAuth が必要です（ローカル環境の場合、`DISCORD_REDIRECT_URI` の設定も必要）。

---

## 4️⃣ リポジトリ構成

```
Jyogi_Navi/
├── apps/
│   ├── web/        # 新入生向けチャットUI（Next.js）
│   ├── api/        # バックエンド API（FastAPI / Python）
│   └── admin/      # 管理画面（Next.js）
├── packages/
│   └── openapi/    # バックエンドから自動生成される TypeScript 型・SDK
├── infra/          # Terraform（Cloudflare リソース管理）
├── docs/           # 設計ドキュメント
├── flake.nix       # Nix 開発環境定義
└── turbo.json      # Turborepo タスク定義
```

詳細は [`docs/06_directory.md`](06_directory.md) を参照。

---

## 5️⃣ 開発フロー

### ブランチ戦略

```
main                    ← 本番デプロイのソース（直接 push 禁止）
└── {名前}/issue{番号}/{概要}   ← 作業ブランチ
  例: Alice/issue52/admin_display_create
```

> ※上記は推奨命名例です。厳密な強制ルールではなく、ある程度柔軟に運用しています。
> チームで分かりやすければ、issue番号や概要だけ・名前なし等でもOKです。

### 作業の流れ

```
1. GitHub Issues でタスクを確認・アサイン
2. main から作業ブランチを切る
   git switch -c Alice/issue99/feature-name
3. 実装・コミット
4. PR を作成（main へ）
5. レビューを受ける
6. Approve されたらマージ
```

### コミットメッセージ規則

[Conventional Commits](https://www.conventionalcommits.org/) に従います：

```
feat: 新機能追加
fix: バグ修正
chore: ビルド・ツール・設定の変更
docs: ドキュメントのみの変更
refactor: 機能変更なしのリファクタリング
test: テストの追加・修正
```

### PR を出す前のチェックリスト

- [ ] `pnpm lint`（FE）/ `uv run ruff check .`（BE）が通っている
- [ ] テストが通っている（`pnpm test` / `uv run pytest`）
- [ ] バックエンドの型・エンドポイントを変更した場合は OpenAPI を再生成した（後述）

---

## 6️⃣ スキーマ駆動開発（重要）

このプロジェクトでは **バックエンドの型定義をフロントエンドで再定義しません**。
FastAPI の Pydantic モデルから OpenAPI スキーマを生成し、TypeScript の型・SDK クライアントを自動生成しています。

```
apps/api（Pydantic モデル）
  → apps/api/openapi.json         ← 自動生成
    → packages/openapi/src/client/ ← 自動生成（TypeScript 型・SDK）
```

### バックエンドを変更したら必ず実行

```bash
# OpenAPI スキーマと TypeScript クライアントを再生成
pnpm openapi

# 生成されたファイルもコミットに含める
git add apps/api/openapi.json packages/openapi/src/client/
```

### フロントエンドでの使い方

```ts
// 型は @jyogi-navi/openapi/types からインポート（独自定義しない）
import type { UserResponse, UserRole } from "@jyogi-navi/openapi/types";

// SDK（TanStack Query）
import { useQuery } from "@tanstack/react-query";
import { adminStatsApiAdminStatsGetOptions } from "@jyogi-navi/openapi/react-query";

const { data } = useQuery(adminStatsApiAdminStatsGetOptions());
```

> CI（`check-openapi.yml`）が再生成して差分をチェックします。コミット漏れがあると CI が失敗します。

詳細は [`docs/schema-driven.md`](schema-driven.md) を参照。

---

## 7️⃣ よく使うコマンド

| コマンド | 説明 |
|---|---|
| `pnpm install` | Node.js 依存パッケージのインストール |
| `pnpm dev` | 全アプリを同時に開発サーバー起動 |
| `pnpm --filter web dev` | apps/web のみ起動 |
| `pnpm --filter admin dev` | apps/admin のみ起動 |
| `pnpm lint` | 全 FE の Lint 実行 |
| `pnpm openapi` | OpenAPI スキーマ・TS クライアント再生成 |
| `uv run uvicorn main:app --reload --port 8080` | API サーバー起動 |
| `uv run pytest` | バックエンドテスト実行 |
| `uv run ruff check .` | バックエンド Lint 実行 |
| `uv run ruff format .` | バックエンドフォーマット実行 |

---

## 8️⃣ ドキュメント一覧

| ファイル | 内容 |
|---|---|
| [`docs/01_feature-list.md`](01_feature-list.md) | 機能一覧・優先度 |
| [`docs/02_tech-stack.md`](02_tech-stack.md) | 技術スタック選定理由 |
| [`docs/03_screen-flow.md`](03_screen-flow.md) | 画面フロー |
| [`docs/04_permission-design.md`](04_permission-design.md) | 権限設計（RBAC） |
| [`docs/05_erd.md`](05_erd.md) | ER 図 |
| [`docs/06_directory.md`](06_directory.md) | ディレクトリ構成詳細 |
| [`docs/07_infrastructure.md`](07_infrastructure.md) | インフラ構成 |
| [`docs/08_logging.md`](08_logging.md) | ログ設計 |
| [`docs/09_schedule_and_issues.md`](09_schedule_and_issues.md) | スプリント・Issue 管理 |
| [`docs/nix-setup.md`](nix-setup.md) | Nix 環境セットアップ詳細 |
| [`docs/schema-driven.md`](schema-driven.md) | スキーマ駆動開発フロー |

---

## 9️⃣ 困ったときは

- **Discord** でチームに質問する
- **GitHub Issues** で「question」ラベルを付けて起票する
- ドキュメントに誤りや不足があれば PR を出してください
