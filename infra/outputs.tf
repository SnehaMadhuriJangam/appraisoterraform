output "cloud_run_url" {
  description = "The deployed Cloud Run service URL"
  value       = google_cloud_run_v2_service.app.uri
}

output "service_name" {
  description = "Name of the deployed service"
  value       = google_cloud_run_v2_service.app.name
}

output "bucket_narratives" {
  description = "Action Item Narratives Bucket"
  value       = google_storage_bucket.action_item_narratives.name
}

output "bucket_audit_reports" {
  description = "Appraiso Audit Reports Bucket"
  value       = google_storage_bucket.appraiso_audit_reports.name
}

output "bucket_multimedia" {
  description = "Smart Audit Multimedia Bucket"
  value       = google_storage_bucket.smart_audit_multimedia.name
}
