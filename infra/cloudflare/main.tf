# Cloudflare Workers のスクリプト自体は wrangler deploy (CI) で管理する。
# このファイルでは将来のカスタムドメイン・DNS・KV 等の周辺リソース管理の土台として使用する。
#
# Workers プロジェクトは初回の wrangler deploy 時に自動作成される:
#   - jyogi-navi-web  (apps/web)
#   - jyogi-navi-admin (apps/admin)

# GitHub Actions Secrets
resource "github_actions_secret" "cloudflare_api_token" {
  repository  = var.github_repo
  secret_name = "CLOUDFLARE_API_TOKEN"
  plaintext_value = var.cloudflare_api_token
}

resource "github_actions_secret" "cloudflare_account_id" {
  repository  = var.github_repo
  secret_name = "CLOUDFLARE_ACCOUNT_ID"
  plaintext_value = var.cloudflare_account_id
}
