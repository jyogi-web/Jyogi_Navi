# GitHub Actions Secrets を一元管理するモジュール。
# Cloudflare 用と GCP 用の両方を管理する。

# ============================================================
# Cloudflare 用 GitHub Actions Secrets
# ============================================================
resource "github_actions_secret" "cloudflare_api_token" {
  repository      = var.github_repo
  secret_name     = "CLOUDFLARE_API_TOKEN"
  plaintext_value = var.cloudflare_api_token
}

resource "github_actions_secret" "cloudflare_account_id" {
  repository      = var.github_repo
  secret_name     = "CLOUDFLARE_ACCOUNT_ID"
  plaintext_value = var.cloudflare_account_id
}

# ============================================================
# GCP 用 GitHub Actions Secrets（deploy-api.yml で使用）
# ============================================================
resource "github_actions_secret" "gcp_workload_identity_provider" {
  repository      = var.github_repo
  secret_name     = "GCP_WORKLOAD_IDENTITY_PROVIDER"
  plaintext_value = var.gcp_workload_identity_provider
}

resource "github_actions_secret" "gcp_service_account" {
  repository      = var.github_repo
  secret_name     = "GCP_SERVICE_ACCOUNT"
  plaintext_value = var.gcp_service_account
}

resource "github_actions_secret" "gcp_project_id" {
  repository      = var.github_repo
  secret_name     = "GCP_PROJECT_ID"
  plaintext_value = var.gcp_project_id
}

resource "github_actions_secret" "gcp_region" {
  repository      = var.github_repo
  secret_name     = "GCP_REGION"
  plaintext_value = var.gcp_region
}

resource "github_actions_secret" "tidb_port" {
  repository      = var.github_repo
  secret_name     = "TIDB_PORT"
  plaintext_value = var.tidb_port
}

resource "github_actions_secret" "daily_token_limit" {
  repository      = var.github_repo
  secret_name     = "DAILY_TOKEN_LIMIT"
  plaintext_value = var.daily_token_limit
}
