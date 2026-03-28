variable "github_token" {
  description = "GitHub Personal Access Token（repo の secrets 書き込み権限）。Fine-grained PAT: Secrets Read and write。Classic PAT: repo スコープ"
  type        = string
  sensitive   = true
}

variable "github_owner" {
  description = "GitHub organization or user name"
  type        = string
  default     = "jyogi-web"
}

variable "github_repo" {
  description = "GitHub repository name"
  type        = string
  default     = "Jyogi_Navi"
}

# Cloudflare 関連
variable "cloudflare_api_token" {
  description = "Cloudflare API Token（Workers 編集権限）"
  type        = string
  sensitive   = true
}

variable "cloudflare_account_id" {
  description = "Cloudflare Account ID"
  type        = string
}

# GCP 関連
variable "gcp_workload_identity_provider" {
  description = "GCP Workload Identity Provider のリソース名（infra/gcp の outputs.workload_identity_provider）"
  type        = string
}

variable "gcp_service_account" {
  description = "GitHub Actions 用 GCP Service Account のメールアドレス（infra/gcp の outputs.service_account_email）"
  type        = string
}

variable "gcp_project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "gcp_region" {
  description = "GCP Region（例: asia-northeast1）"
  type        = string
  default     = "asia-northeast1"
}

variable "tidb_port" {
  description = "TiDB Serverless ポート番号"
  type        = string
  default     = "4000"
}

variable "daily_token_limit" {
  description = "1日あたりの最大トークン数"
  type        = string
  default     = "10000"
}
