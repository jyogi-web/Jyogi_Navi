variable "gcp_project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "gcp_region" {
  description = "GCP Region（例: asia-northeast1）"
  type        = string
  default     = "asia-northeast1"
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

# Secret Manager に格納する機密値
variable "tidb_host" {
  description = "TiDB Serverless ホスト名"
  type        = string
  sensitive   = true
}

variable "tidb_user" {
  description = "TiDB Serverless ユーザー名"
  type        = string
  sensitive   = true
}

variable "tidb_password" {
  description = "TiDB Serverless パスワード"
  type        = string
  sensitive   = true
}

variable "tidb_database" {
  description = "TiDB データベース名"
  type        = string
  sensitive   = true
}

variable "tidb_ssl_ca" {
  description = "TiDB SSL CA 証明書のパス（本番環境）"
  type        = string
  default     = "/etc/ssl/certs/ca-certificates.crt"
}

variable "supabase_url" {
  description = "Supabase Project URL"
  type        = string
  sensitive   = true
}

variable "supabase_secret" {
  description = "Supabase Service Role Key"
  type        = string
  sensitive   = true
}

variable "dify_api_base_url" {
  description = "Dify Chat API のベース URL"
  type        = string
  sensitive   = true
}

variable "dify_api_key" {
  description = "Dify API キー"
  type        = string
  sensitive   = true
}

variable "discord_client_id" {
  description = "Discord OAuth Client ID"
  type        = string
  sensitive   = true
}

variable "discord_client_secret" {
  description = "Discord OAuth Client Secret"
  type        = string
  sensitive   = true
}

variable "discord_guild_id" {
  description = "Discord Guild（サーバー）ID"
  type        = string
  sensitive   = true
}

variable "allowed_origins" {
  description = "CORS 許可オリジン（カンマ区切り。例: https://example.com,https://admin.example.com）"
  type        = string
  sensitive   = true
}
