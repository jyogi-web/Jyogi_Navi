# ============================================================
# Artifact Registry
# ============================================================
resource "google_artifact_registry_repository" "api" {
  repository_id = "jyogi-navi"
  location      = var.gcp_region
  format        = "DOCKER"
  description   = "Docker images for jyogi-navi API"
}

# ============================================================
# Workload Identity Federation（GitHub Actions OIDC 連携）
# ============================================================
resource "google_iam_workload_identity_pool" "github" {
  workload_identity_pool_id = "github-actions"
  display_name              = "GitHub Actions"
  description               = "Workload Identity Pool for GitHub Actions"
}

resource "google_iam_workload_identity_pool_provider" "github" {
  workload_identity_pool_id          = google_iam_workload_identity_pool.github.workload_identity_pool_id
  workload_identity_pool_provider_id = "github-provider"
  display_name                       = "GitHub OIDC Provider"

  oidc {
    issuer_uri = "https://token.actions.githubusercontent.com"
  }

  attribute_mapping = {
    "google.subject"       = "assertion.sub"
    "attribute.actor"      = "assertion.actor"
    "attribute.repository" = "assertion.repository"
  }

  attribute_condition = "assertion.repository == '${var.github_owner}/${var.github_repo}'"
}

# ============================================================
# Service Account（GitHub Actions デプロイ用）
# ============================================================
resource "google_service_account" "github_actions" {
  account_id   = "github-actions-deploy"
  display_name = "GitHub Actions Deploy"
  description  = "Service account used by GitHub Actions to deploy to Cloud Run"
}

# ============================================================
# Service Account（Cloud Run ランタイム用）
# ============================================================
resource "google_service_account" "cloud_run_runtime" {
  account_id   = "cloud-run-api-runtime"
  display_name = "Cloud Run API Runtime"
  description  = "Service account for Cloud Run API runtime (minimum required permissions only)"
}

# ランタイム SA に Secret Manager アクセス権限のみ付与
resource "google_project_iam_member" "runtime_sm_accessor" {
  project = var.gcp_project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.cloud_run_runtime.email}"
}

# WIF からデプロイ用 SA を借用する権限を付与
resource "google_service_account_iam_member" "wif_impersonation" {
  service_account_id = google_service_account.github_actions.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "principalSet://iam.googleapis.com/${google_iam_workload_identity_pool.github.name}/attribute.repository/${var.github_owner}/${var.github_repo}"
}

resource "google_project_iam_member" "run_admin" {
  project = var.gcp_project_id
  role    = "roles/run.admin"
  member  = "serviceAccount:${google_service_account.github_actions.email}"
}

resource "google_project_iam_member" "ar_writer" {
  project = var.gcp_project_id
  role    = "roles/artifactregistry.writer"
  member  = "serviceAccount:${google_service_account.github_actions.email}"
}

# デプロイ用 SA がランタイム SA を Cloud Run に割り当てるための権限
# プロジェクト全体ではなくランタイム SA に対してのみ付与（最小権限）
resource "google_service_account_iam_member" "sa_user" {
  service_account_id = google_service_account.cloud_run_runtime.name
  role               = "roles/iam.serviceAccountUser"
  member             = "serviceAccount:${google_service_account.github_actions.email}"
}

# ============================================================
# Secret Manager（機密環境変数 / 5 secrets = 無料枠内）
# 各 secret は関連する値を JSON でまとめて1つの secret に格納する
# apps/api/config.py の model_validator が JSON を個別フィールドに展開する
# ============================================================
locals {
  secrets = {
    TIDB_CONFIG = jsonencode({
      host     = var.tidb_host
      user     = var.tidb_user
      password = var.tidb_password
      database = var.tidb_database
      ssl_ca   = var.tidb_ssl_ca
    })
    SUPABASE_CONFIG = jsonencode({
      url    = var.supabase_url
      secret = var.supabase_secret
    })
    DIFY_CONFIG = jsonencode({
      api_base_url = var.dify_api_base_url
      api_key      = var.dify_api_key
    })
    DISCORD_CONFIG = jsonencode({
      client_id     = var.discord_client_id
      client_secret = var.discord_client_secret
      guild_id      = var.discord_guild_id
    })
    ALLOWED_ORIGINS = var.allowed_origins
  }
}

resource "google_secret_manager_secret" "api_secrets" {
  for_each  = local.secrets
  secret_id = each.key

  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "api_secrets" {
  for_each    = local.secrets
  secret      = google_secret_manager_secret.api_secrets[each.key].id
  secret_data = each.value
}

# ============================================================
# Cloud Run（jyogi-navi-api）
# ============================================================
resource "google_cloud_run_v2_service" "api" {
  name     = "jyogi-navi-api"
  location = var.gcp_region

  deletion_protection = false

  template {
    scaling {
      min_instance_count = 0
      max_instance_count = 3
    }

    service_account = google_service_account.cloud_run_runtime.email

    containers {
      # イメージは GitHub Actions が deploy-api.yml でデプロイ時に更新する
      # 初回 terraform apply では placeholder を使用し、以降は CI/CD に任せる
      image = "${var.gcp_region}-docker.pkg.dev/${var.gcp_project_id}/jyogi-navi/api:latest"

      ports {
        container_port = 8080
      }

      resources {
        limits = {
          memory = "512Mi"
          cpu    = "1"
        }
      }

      env {
        name  = "APP_ENV"
        value = "production"
      }

      dynamic "env" {
        for_each = local.secrets
        content {
          name = env.key
          value_source {
            secret_key_ref {
              secret  = google_secret_manager_secret.api_secrets[env.key].secret_id
              version = "latest"
            }
          }
        }
      }
    }
  }
}

# 未認証アクセスを許可（フロントエンドから呼び出すため）
resource "google_cloud_run_v2_service_iam_member" "public_access" {
  project  = var.gcp_project_id
  location = var.gcp_region
  name     = google_cloud_run_v2_service.api.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}
