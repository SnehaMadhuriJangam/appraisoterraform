terraform {
  required_version = ">= 1.5.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
  # Backend configuration passed dynamically via CLI (or GitHub Actions)
    # Tells Terraform: "Don't save state on disk; use a Google Cloud Storage bucket"
  backend "gcs" {}
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Cloud Run v2 Service
resource "google_cloud_run_v2_service" "app" {
  name     = var.service_name
  location = var.region
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    containers {
      image = var.container_image
      resources {
        limits = {
          cpu    = "1000m"
          memory = "512Mi"
        }
      }
      env {
        name  = "ENVIRONMENT"
        value = "demo"
      }
      env {
        name  = "PROJECT_ID"
        value = var.project_id
      }
    }
    scaling {
      min_instance_count = 0
      max_instance_count = 2
    }
  }
}

# Allow public unauthenticated access so you can verify the URL in browser
resource "google_cloud_run_v2_service_iam_member" "public_access" {
  name     = google_cloud_run_v2_service.app.name
  location = google_cloud_run_v2_service.app.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}
