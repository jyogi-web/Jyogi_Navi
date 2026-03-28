# Cloudflare Workers のスクリプト自体は wrangler deploy (CI) で管理する。
# このファイルでは将来のカスタムドメイン・DNS・KV 等の周辺リソース管理の土台として使用する。
#
# Workers プロジェクトは初回の wrangler deploy 時に自動作成される:
#   - jyogi-navi-web  (apps/web)
#   - jyogi-navi-admin (apps/admin)
#
# GitHub Actions Secrets は infra/github/ で一元管理する。
