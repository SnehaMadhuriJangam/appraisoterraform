output "evidence_bucket_name" {
  description = "Name of the Evidence Bucket (DC-01)"
  value       = google_storage_bucket.evidence_bucket.name
}

output "quarantine_bucket_name" {
  description = "Name of the Quarantine Bucket (DC-12)"
  value       = google_storage_bucket.quarantine_bucket.name
}
