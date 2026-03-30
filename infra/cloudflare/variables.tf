variable "cloudflare_account_id" {
  description = "Cloudflare Account ID"
  type        = string
}

variable "cloudflare_api_token" {
  description = "Cloudflare API Token (Workers 編集権限)"
  type        = string
  sensitive   = true
}

variable "github_token" {
  description = "GitHub Personal Access Token (repo の secrets 書き込み権限)"
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
