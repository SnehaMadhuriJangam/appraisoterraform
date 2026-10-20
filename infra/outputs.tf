output "cloud_run_url" {
  description = "The deployed Cloud Run service URL"
  value       = google_cloud_run_v2_service.app.uri
}

output "service_name" {
  description = "Name of the deployed service"
  value       = google_cloud_run_v2_service.app.name
}
