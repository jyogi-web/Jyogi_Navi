# iac

作成日時: 2026年3月27日
最終更新日時: 2026年3月27日

# IaC（Infrastructure as Code）ガイド

---

## 概要

本プロジェクトのインフラ管理は **Terraform** と **GitHub Actions** の組み合わせで構成されています。

| 管理対象 | 方法 | 場所 |
|---|---|---|
| Cloudflare 周辺リソース（DNS・GitHub Secrets） | Terraform | `infra/cloudflare/` |
| Cloudflare Workers デプロイ（FE） | Wrangler (GitHub Actions) | `.github/workflows/deploy-fe.yml` |
| Dify（RAG オーケストレーター） | Docker Compose | `infra/dify/` |
| Backend API（Cloud Run） | GitHub Actions | `.github/workflows/ci-BE.yml` |

---

## ディレクトリ構成

```
infra/
├── cloudflare/          # Terraform: Cloudflare 周辺リソース
│   ├── main.tf          # GitHub Actions Secrets 等のリソース定義
│   ├── variables.tf     # 入力変数定義
│   ├── outputs.tf       # 出力値定義
│   └── versions.tf      # Provider バージョン固定
└── dify/                # Docker Compose: Dify セルフホスト
    ├── docker-compose.yml
    └── SETUP.md         # セットアップ手順
```

---

## 1. Terraform（Cloudflare / GitHub 周辺）

### 対象リソース

現在 Terraform で管理しているリソースは以下の通りです。

| リソース | 説明 |
|---|---|
| `github_actions_secret.cloudflare_api_token` | `CLOUDFLARE_API_TOKEN` を GitHub Secrets へ登録 |
| `github_actions_secret.cloudflare_account_id` | `CLOUDFLARE_ACCOUNT_ID` を GitHub Secrets へ登録 |

> **Note:** Cloudflare Workers のプロジェクト自体（`jyogi-navi-web` / `jyogi-navi-admin`）は初回 `wrangler deploy` 時に自動作成されます。カスタムドメイン・DNS・KV 等を追加する場合はここで管理します。

### Provider バージョン

```hcl
terraform {
  required_version = ">= 1.0"
  required_providers {
    cloudflare = {
      source  = "cloudflare/cloudflare"
      version = "~> 5.0"
    }
    github = {
      source  = "integrations/github"
      version = "~> 6.0"
    }
  }
}
```

### 変数一覧

| 変数名 | 型 | sensitive | 説明 |
|---|---|---|---|
| `cloudflare_account_id` | string | false | Cloudflare Account ID |
| `cloudflare_api_token` | string | **true** | Cloudflare API Token（Workers 編集権限） |
| `github_token` | string | **true** | GitHub PAT（repo の secrets 書き込み権限） |
| `github_owner` | string | false | GitHub org / user 名（default: `jyogi-web`） |
| `github_repo` | string | false | リポジトリ名（default: `Jyogi_Navi`） |

### 初回セットアップ手順

```bash
cd infra/cloudflare

# 1. terraform.tfvars を作成（.gitignore 済み）
cat > terraform.tfvars <<EOF
cloudflare_account_id = "<your-account-id>"
cloudflare_api_token  = "<your-api-token>"
github_token          = "<your-github-pat>"
EOF

# 2. 初期化
terraform init

# 3. 差分確認
terraform plan

# 4. 適用
terraform apply
```

> **重要:** `terraform.tfvars` には機密情報が含まれるため、絶対に Git へコミットしないでください。`.gitignore` に含まれていることを確認してください。

### 運用

- インフラ変更は必ず `terraform plan` で差分を確認してから `apply` する
- State ファイルはローカル管理のため、複数人で作業する場合は実行タイミングを調整する（将来的に Terraform Cloud / GCS Backend への移行を推奨）

---

## 2. Cloudflare Workers デプロイ（GitHub Actions + Wrangler）

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

#### 必要な GitHub Secrets

| Secret 名 | 用途 | 設定方法 |
|---|---|---|
| `CLOUDFLARE_API_TOKEN` | Wrangler デプロイ認証 | Terraform で自動設定 |
| `CLOUDFLARE_ACCOUNT_ID` | デプロイ先アカウント指定 | Terraform で自動設定 |

#### Cloudflare Workers プロジェクト名

| アプリ | Workers プロジェクト名 |
|---|---|
| `apps/web` | `jyogi-navi-web` |
| `apps/admin` | `jyogi-navi-admin` |

---

## 3. Dify（Docker Compose）

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

## 4. Backend API（Cloud Run）

Cloud Run へのデプロイは `.github/workflows/ci-BE.yml` で管理します。GitHub Actions（cloud-hosted）から Google Cloud Run へ自動デプロイされます。

詳細は `ci-BE.yml` および `docs/07_infrastructure.md` を参照してください。

---

## Secret 管理方針

| Secret | 管理方法 |
|---|---|
| `CLOUDFLARE_API_TOKEN` | Terraform → GitHub Actions Secrets |
| `CLOUDFLARE_ACCOUNT_ID` | Terraform → GitHub Actions Secrets |
| Dify 関連（DB・Redis・API キー等） | `infra/dify/.env`（ローカル管理、Git 非コミット） |
| Google Cloud 認証情報 | GitHub Actions Secrets（手動設定） |

> `infra/dify/.env` は `.gitignore` 対象です。`infra/dify/.env.example` をコピーして使用してください。

---

## 将来の課題

- Terraform State の Remote Backend 化（GCS / Terraform Cloud）
- Cloudflare DNS・カスタムドメイン管理の Terraform 化
- GitHub Actions Secrets の追加分（GCP 認証情報等）の Terraform 管理への統合
