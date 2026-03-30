# IaC（Infrastructure as Code）ガイド

作成日時: 2026年3月27日
最終更新日時: 2026年3月28日

---

## 概要

本プロジェクトのインフラ管理は **Terraform** と **GitHub Actions** の組み合わせで構成されています。

| 管理対象 | 方法 | 場所 |
|---|---|---|
| Cloudflare 周辺リソース（DNS・カスタムドメイン等、将来用） | Terraform | `infra/cloudflare/` |
| GCP リソース（AR・WIF・SA・Secret Manager・Cloud Run） | Terraform | `infra/gcp/` |
| GitHub Actions Secrets（CF + GCP 両方） | Terraform | `infra/github/` |
| Cloudflare Workers デプロイ（FE） | Wrangler (GitHub Actions) | `.github/workflows/deploy-fe.yml` |
| Backend API デプロイ（Cloud Run） | GitHub Actions | `.github/workflows/deploy-api.yml` |
| Dify（RAG オーケストレーター） | Docker Compose | `infra/dify/` |

---

## ディレクトリ構成

```
infra/
├── cloudflare/          # Terraform: Cloudflare 周辺リソース（将来用）
│   ├── main.tf          # カスタムドメイン・DNS・KV 等（現在はプレースホルダー）
│   ├── variables.tf     # CF 固有の変数
│   ├── outputs.tf
│   └── versions.tf      # cloudflare provider のみ
├── gcp/                 # Terraform: GCP リソース一式
│   ├── main.tf          # AR / WIF / SA / Secret Manager / Cloud Run
│   ├── variables.tf
│   ├── outputs.tf
│   └── versions.tf      # google provider のみ
├── github/              # Terraform: GitHub Actions Secrets（全サービス分）
│   ├── main.tf          # CF + GCP 両方の Secrets
│   ├── variables.tf
│   ├── outputs.tf
│   └── versions.tf      # github provider のみ
└── dify/                # Docker Compose: Dify セルフホスト
    ├── docker-compose.yml
    └── SETUP.md         # セットアップ手順
```

---

## 1. Terraform（Cloudflare 周辺）

将来のカスタムドメイン・DNS・KV 等の管理用モジュール。
現在は Cloudflare Workers プロジェクト自体は初回 `wrangler deploy` 時に自動作成されるため、リソース定義は空です。

### Provider バージョン

| Provider | バージョン制約 |
|---|---|
| `cloudflare/cloudflare` | `~> 5.0` |

### 変数一覧

| 変数名 | 型 | sensitive | 説明 |
|---|---|---|---|
| `cloudflare_account_id` | string | false | Cloudflare Account ID |
| `cloudflare_api_token` | string | **true** | Cloudflare API Token（Workers 編集権限） |

---

## 2. Terraform（GCP）

Cloud Run バックエンド API に必要な GCP リソースをすべて Terraform で管理します。

### 対象リソース

| リソース | 説明 |
|---|---|
| `google_artifact_registry_repository.api` | Docker イメージリポジトリ（`jyogi-navi`） |
| `google_iam_workload_identity_pool.github` | GitHub Actions OIDC 用 WIF プール |
| `google_iam_workload_identity_pool_provider.github` | GitHub OIDC プロバイダー |
| `google_service_account.github_actions` | GitHub Actions デプロイ用 SA |
| `google_project_iam_member.*` | SA への IAM ロール付与（run.admin / ar.writer / sa.user / sm.accessor） |
| `google_secret_manager_secret.*` | 機密環境変数 13 個 |
| `google_secret_manager_secret_version.*` | 各 Secret の初期値 |
| `google_cloud_run_v2_service.api` | Cloud Run サービス（`jyogi-navi-api`） |
| `google_cloud_run_v2_service_iam_member.public_access` | 未認証アクセス許可 |

### Provider バージョン

| Provider | バージョン制約 |
|---|---|
| `hashicorp/google` | `~> 6.0` |

### 変数一覧

| 変数名 | 型 | sensitive | 説明 |
|---|---|---|---|
| `gcp_project_id` | string | false | GCP Project ID |
| `gcp_region` | string | false | GCP Region（default: `asia-northeast1`） |
| `github_owner` | string | false | GitHub org（default: `jyogi-web`） |
| `github_repo` | string | false | リポジトリ名（default: `Jyogi_Navi`） |
| `tidb_host` | string | **true** | TiDB Serverless ホスト名 |
| `tidb_user` | string | **true** | TiDB Serverless ユーザー名 |
| `tidb_password` | string | **true** | TiDB Serverless パスワード |
| `tidb_database` | string | **true** | データベース名 |
| `tidb_ssl_ca` | string | false | SSL CA パス |
| `supabase_url` | string | **true** | Supabase Project URL |
| `supabase_secret` | string | **true** | Supabase Service Role Key |
| `dify_api_base_url` | string | **true** | Dify Chat API ベース URL |
| `dify_api_key` | string | **true** | Dify API キー |
| `discord_client_id` | string | **true** | Discord OAuth Client ID |
| `discord_client_secret` | string | **true** | Discord OAuth Client Secret |
| `discord_guild_id` | string | **true** | Discord Guild ID |
| `allowed_origins` | string | **true** | CORS 許可オリジン（カンマ区切り） |

### Outputs

`terraform output` で以下の値を確認できます。`infra/github/` の `terraform.tfvars` にコピーして使用してください。

| Output | 説明 |
|---|---|
| `workload_identity_provider` | `GCP_WORKLOAD_IDENTITY_PROVIDER` に設定する値 |
| `service_account_email` | `GCP_SERVICE_ACCOUNT` に設定する値 |
| `artifact_registry_url` | Docker イメージの push 先 URL |
| `cloud_run_url` | Cloud Run サービスの URL |

### terraform.tfvars の生成（推奨）

`.env` ファイルがある場合は、`apps/api/scripts/gen_secret_payloads.py` を使うと
`infra/gcp/terraform.tfvars` を自動生成できます。

```bash
# apps/api/ ディレクトリで実行する（uv run はここから呼ぶ必要がある）
cd apps/api

# 内容を標準出力で確認するだけ（ファイルは生成しない）
uv run python scripts/gen_secret_payloads.py --env .env

# terraform.tfvars を直接生成する
uv run python scripts/gen_secret_payloads.py --env .env --write-tfvars
```

生成後、`infra/gcp/terraform.tfvars` を開いて `gcp_project_id` を手動で設定してください
（スクリプトはこの値を知らないためコメントアウトされた状態で出力されます）。

> **注意:** `terraform.tfvars` は `.gitignore` 済みです。Git にはコミットされません。

### 初回セットアップ手順

```bash
cd infra/gcp

# 1. terraform.tfvars を作成
#    方法A: スクリプトで自動生成（推奨、上記「terraform.tfvars の生成」参照）
#    方法B: テンプレートをコピーして手動で値を埋める
cp terraform.tfvars.example terraform.tfvars
# terraform.tfvars を編集して各値を設定する（.gitignore 済みのため Git にはコミットされない）

# 2. GCP API を有効化（初回のみ）
gcloud services enable \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  secretmanager.googleapis.com \
  iam.googleapis.com \
  iamcredentials.googleapis.com \
  --project=<your-project-id>

# 3. 初期化
terraform init

# 4. 差分確認
terraform plan

# 5. 適用
terraform apply
```

---

## 3. Terraform（GitHub Actions Secrets）

Cloudflare・GCP 両方の GitHub Actions Secrets を一元管理します。

### 対象リソース

| リソース（Secret 名） | 用途 | 設定方法 |
|---|---|---|
| `CLOUDFLARE_API_TOKEN` | Wrangler デプロイ認証 | Terraform で自動設定 |
| `CLOUDFLARE_ACCOUNT_ID` | デプロイ先アカウント指定 | Terraform で自動設定 |
| `GCP_WORKLOAD_IDENTITY_PROVIDER` | WIF プロバイダー（OIDC 認証） | Terraform で自動設定 |
| `GCP_SERVICE_ACCOUNT` | デプロイ用 SA メール | Terraform で自動設定 |
| `GCP_PROJECT_ID` | GCP プロジェクト ID | Terraform で自動設定 |
| `GCP_REGION` | GCP リージョン | Terraform で自動設定 |
| `TIDB_PORT` | TiDB ポート番号（非機密） | Terraform で自動設定 |
| `DAILY_TOKEN_LIMIT` | 1日あたり最大トークン数 | Terraform で自動設定 |

### Provider バージョン

| Provider | バージョン制約 | 実際のインストール済みバージョン |
|---|---|---|
| `integrations/github` | `~> 6.0` | v6.11.1 |

### 変数一覧

| 変数名 | 型 | sensitive | 説明 |
|---|---|---|---|
| `github_token` | string | **true** | GitHub PAT。Fine-grained PAT: `Secrets: Read and write`。Classic PAT: `repo` スコープ |
| `github_owner` | string | false | GitHub org（default: `jyogi-web`） |
| `github_repo` | string | false | リポジトリ名（default: `Jyogi_Navi`） |
| `cloudflare_api_token` | string | **true** | Cloudflare API Token |
| `cloudflare_account_id` | string | false | Cloudflare Account ID |
| `gcp_workload_identity_provider` | string | false | `infra/gcp` の `outputs.workload_identity_provider` の値 |
| `gcp_service_account` | string | false | `infra/gcp` の `outputs.service_account_email` の値 |
| `gcp_project_id` | string | false | GCP Project ID |
| `gcp_region` | string | false | GCP Region（default: `asia-northeast1`） |
| `tidb_port` | string | false | TiDB ポート（default: `4000`） |
| `daily_token_limit` | string | false | トークン上限（default: `10000`） |

### 初回セットアップ手順

> **前提:** `infra/gcp/` を先に apply して outputs を取得してください。

```bash
cd infra/github

# 1. infra/gcp の outputs を確認（terraform.tfvars に転記する値を取得）
cd ../gcp && terraform output
cd ../github

# 2. terraform.tfvars を作成（テンプレートをコピーして値を埋める）
cp terraform.tfvars.example terraform.tfvars
# terraform.tfvars を編集して各値を設定する（.gitignore 済みのため Git にはコミットされない）

# 2. 初期化
terraform init

# 3. 差分確認
terraform plan

# 4. 適用
terraform apply
```

---

## 4. Cloudflare Workers デプロイ（GitHub Actions + Wrangler）

### ワークフロー: `deploy-fe.yml`

`main` ブランチへのプッシュ時、変更検知に基づいて `apps/web` / `apps/admin` を自動デプロイします。

```
トリガー: push to main
  ↓
detect-changes ジョブ（dorny/paths-filter）
  ├─ apps/web/** に変更あり → deploy-web ジョブ
  └─ apps/admin/** に変更あり → deploy-admin ジョブ
```

#### deploy-web / deploy-admin の処理フロー

1. `pnpm install --frozen-lockfile`
2. `pnpm turbo run build --filter=<app>` — Next.js ビルド
3. `pnpm --filter <app> build:pages` — OpenNext（Cloudflare Workers 向け）ビルド
4. `cloudflare/wrangler-action@v3 deploy` — Cloudflare Workers へデプロイ

#### Cloudflare Workers プロジェクト名

| アプリ | Workers プロジェクト名 |
|---|---|
| `apps/web` | `jyogi-navi-web` |
| `apps/admin` | `jyogi-navi-admin` |

---

## 5. Backend API デプロイ（GitHub Actions → Cloud Run）

### ワークフロー: `deploy-api.yml`

`main` ブランチへのプッシュ時、`apps/api/**` の変更検知に基づいて Cloud Run へ自動デプロイします。

```
トリガー: push to main
  ↓
detect-changes ジョブ（dorny/paths-filter）
  ↓ apps/api/** に変更あり
build-push ジョブ
  1. google-github-actions/auth@v2（WIF 認証）
  2. Docker build（apps/api/Dockerfile）
  3. Artifact Registry へ push（タグ: git SHA + latest）
  ↓
deploy ジョブ
  1. google-github-actions/auth@v2（WIF 認証）
  2. google-github-actions/deploy-cloudrun@v2
     - サービス名: jyogi-navi-api
     - ポート: 8080
     - 環境変数: GCP Secret Manager 経由で注入
```

#### Artifact Registry イメージパス

```
<GCP_REGION>-docker.pkg.dev/<GCP_PROJECT_ID>/jyogi-navi/api:<git-sha>
```

#### 必要な GitHub Actions Secrets

`infra/github/` の Terraform で自動設定されます。

| Secret 名 | 用途 |
|---|---|
| `GCP_WORKLOAD_IDENTITY_PROVIDER` | WIF プロバイダー（OIDC 認証） |
| `GCP_SERVICE_ACCOUNT` | デプロイ用 SA メール |
| `GCP_PROJECT_ID` | GCP プロジェクト ID |
| `GCP_REGION` | GCP リージョン |
| `TIDB_PORT` | TiDB ポート番号（非機密） |
| `DAILY_TOKEN_LIMIT` | 1日あたり最大トークン数（非機密） |

#### GCP Secret Manager で管理する機密値

`infra/gcp/` の Terraform で自動作成・管理されます。Cloud Run 起動時に環境変数として注入されます。

| Secret 名 | 説明 |
|---|---|
| `TIDB_HOST` | TiDB Serverless ホスト名 |
| `TIDB_USER` | TiDB Serverless ユーザー名 |
| `TIDB_PASSWORD` | TiDB Serverless パスワード |
| `TIDB_DATABASE` | データベース名 |
| `TIDB_SSL_CA` | SSL CA パス |
| `SUPABASE_URL` | Supabase Project URL |
| `SUPABASE_SECRET` | Supabase Service Role Key |
| `DIFY_API_BASE_URL` | Dify Chat API ベース URL |
| `DIFY_API_KEY` | Dify API キー |
| `DISCORD_CLIENT_ID` | Discord OAuth Client ID |
| `DISCORD_CLIENT_SECRET` | Discord OAuth Client Secret |
| `DISCORD_GUILD_ID` | Discord Guild ID |
| `ALLOWED_ORIGINS` | CORS 許可オリジン（カンマ区切り） |

---

## 6. Dify（Docker Compose）

Dify は自宅 PC 上で Docker Compose により運用します。詳細なセットアップ・運用手順は [`infra/dify/SETUP.md`](../infra/dify/SETUP.md) を参照してください。

### 主な外部サービス依存

| サービス | 用途 |
|---|---|
| Supabase (PostgreSQL) | Dify 内部 DB（メタデータ管理） |
| TiDB Serverless | ベクトル DB（RAG 検索） |
| Upstash Redis | タスクキュー・レート制限カウンタ |
| Cloudflare Tunnel | 自宅 PC を HTTPS で外部公開 |

### 自動デプロイ

`main` ブランチへのプッシュ時、GitHub Actions（self-hosted runner）が自宅 PC 上で以下を実行します。

```bash
docker-compose pull && docker-compose up -d
```

---

## Secret 管理方針

| Secret | 管理方法 |
|---|---|
| `CLOUDFLARE_API_TOKEN` | Terraform（`infra/github/`）→ GitHub Actions Secrets |
| `CLOUDFLARE_ACCOUNT_ID` | Terraform（`infra/github/`）→ GitHub Actions Secrets |
| GCP GitHub Actions Secrets（4個） | Terraform（`infra/github/`）→ GitHub Actions Secrets |
| GCP Secret Manager 機密値（13個） | Terraform（`infra/gcp/`）→ GCP Secret Manager → Cloud Run 環境変数 |
| Dify 関連（DB・Redis・API キー等） | `infra/dify/.env`（ローカル管理、Git 非コミット） |

> `infra/*/terraform.tfvars` および `infra/dify/.env` は `.gitignore` 対象です。

---

## 将来の課題

- Terraform State の Remote Backend 化（GCS / Terraform Cloud）
- Cloudflare DNS・カスタムドメイン管理の Terraform 化（`infra/cloudflare/` に追加）
