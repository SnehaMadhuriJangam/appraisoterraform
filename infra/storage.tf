###############################################################################
# CIS 3.1 Compliant Storage Buckets
# Architecture: Appraiso Audit System
# Security controls:
#   - Uniform Bucket-Level Access (CIS GCP 5.2)
#   - Public Access Prevention Enforced (CIS GCP 5.1)
#   - 6-Year Lifecycle Retention Rule (CIS 3.1 Data Protection)
#   - Full Governance Metadata Labels (CIS 3.1 Classification)
###############################################################################

# 1. Action Item Narratives Bucket
resource "google_storage_bucket" "action_item_narratives" {
  name     = "${var.project_id}-action-item-narratives"
  location = var.region

  uniform_bucket_level_access = true
  public_access_prevention    = "enforced"

  labels = {
    record_owner        = "msxi-data-governance"
    technical_custodian = "miracle"
    system_of_record    = "appraiso-narratives-store"
    data_classification = "confidential"
    retention_policy    = "6-years"
    environment         = "dev"
  }

  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      age = 2190 # 6-year working retention assumption
    }
  }
}

# 2. Appraiso Audit Reports Bucket
resource "google_storage_bucket" "appraiso_audit_reports" {
  name     = "${var.project_id}-appraiso-audit-reports"
  location = var.region

  uniform_bucket_level_access = true
  public_access_prevention    = "enforced"

  labels = {
    record_owner        = "msxi-data-governance"
    technical_custodian = "miracle"
    system_of_record    = "appraiso-reports-store"
    data_classification = "confidential"
    retention_policy    = "6-years"
    environment         = "dev"
  }

  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      age = 2190 # 6-year working retention assumption
    }
  }
}

# 3. Smart Audit Multimedia Bucket
resource "google_storage_bucket" "smart_audit_multimedia" {
  name     = "${var.project_id}-smart-audit-multimedia"
  location = var.region

  uniform_bucket_level_access = true
  public_access_prevention    = "enforced"

  labels = {
    record_owner        = "msxi-data-governance"
    technical_custodian = "miracle"
    system_of_record    = "appraiso-multimedia-evidence"
    data_classification = "confidential"
    retention_policy    = "6-years"
    environment         = "dev"
  }

  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      age = 2190 # 6-year working retention assumption
    }
  }
}
