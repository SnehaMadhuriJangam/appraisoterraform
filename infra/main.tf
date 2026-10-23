terraform {
  required_version = ">= 1.3.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
  backend "gcs" {}
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# ==============================================================================
# BUCKET 1: Evidence Bucket (DC-01 / DC-33)
# ==============================================================================
resource "google_storage_bucket" "evidence_bucket" {
  # Globally unique bucket name: project-appraiso-evidence-env
  name                        = "${var.project_id}-appraiso-evidence-${var.environment}"
  location                    = var.region
  storage_class               = "STANDARD"
  
  # CIS 3.3: Ensure no public access is ever possible
  uniform_bucket_level_access = true
  public_access_prevention    = "enforced"

  # Retain history of files in case of accidental overwrite/tampering
  versioning {
    enabled = true
  }

  # CIS 3.4: Automated Retention Policy
  # Rule A: Delete files 365 days after the transaction is completed (CustomTime)
  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      days_since_custom_time = 365
    }
  }

  # Rule B: Clean up old versions of overwritten files after 30 days
  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      num_newer_versions         = 2
      days_since_noncurrent_time = 30
    }
  }

  # CIS 3.2 & CIS 3.7: In-Detail Inventory Labels (Tagged based on Public Access)
  labels = {
    environment            = var.environment
    data_class             = "confidential"
    category_id            = "dc-01"
    managed_by             = "terraform"
    retention_period       = "365_days"
    public_access          = "no"
    confidentiality_status = "confidential"
  }
}

# ==============================================================================
# BUCKET 2: Quarantine Bucket (DC-12)
# ==============================================================================
resource "google_storage_bucket" "quarantine_bucket" {
  name                        = "${var.project_id}-appraiso-quarantine-${var.environment}"
  location                    = var.region
  storage_class               = "STANDARD"

  # CIS 3.3: Strict Lockdown
  uniform_bucket_level_access = true
  public_access_prevention    = "enforced"

  # CIS 3.4: Auto-delete failed or suspicious files after 30 days
  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      age = 30 # Delete 30 days after upload date
    }
  }

  # CIS 3.2 & CIS 3.7: In-Detail Inventory Labels (Tagged based on Public Access)
  labels = {
    environment            = var.environment
    data_class             = "confidential"
    category_id            = "dc-12"
    managed_by             = "terraform"
    retention_period       = "30_days"
    public_access          = "no"
    confidentiality_status = "confidential"
  }
}
