variable "project_id" {
  type        = string
  description = "The GCP project ID"
}

variable "region" {
  type        = string
  description = "The GCP region to deploy to"
  default     = "us-central1"
}

variable "service_name" {
  type        = string
  description = "Name of the Cloud Run service"
  default     = "appraiso-cloudrun-service"
}

variable "container_image" {
  type        = string
  description = "Docker container image to deploy to Cloud Run"
  default     = "us-docker.pkg.dev/cloudrun/container/hello:latest"
}
