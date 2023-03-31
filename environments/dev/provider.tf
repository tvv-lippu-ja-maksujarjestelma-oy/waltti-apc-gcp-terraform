terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.56.0"

    }
  }

  required_version = "~> 1.3"
}

provider "google" {
  project                     = var.project_id
  region                      = var.region
  #impersonate_service_account = var.tf_service_account
}
