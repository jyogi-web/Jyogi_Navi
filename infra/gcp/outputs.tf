output "artifact_registry_url" {
  description = "Artifact Registry リポジトリの URL"
  value       = "${var.gcp_region}-docker.pkg.dev/${var.gcp_project_id}/jyogi-navi"
}

output "workload_identity_provider" {
  description = "GitHub Actions Secrets に設定する GCP_WORKLOAD_IDENTITY_PROVIDER の値"
  value       = google_iam_workload_identity_pool_provider.github.name
}

output "service_account_email" {
  description = "GitHub Actions Secrets に設定する GCP_SERVICE_ACCOUNT の値"
  value       = google_service_account.github_actions.email
}

output "cloud_run_url" {
  description = "Cloud Run サービスの URL"
  value       = google_cloud_run_v2_service.api.uri
}
