terraform {
  required_providers {
    google = {
      source = "hashicorp/google"
      # Provider version is resolved from used modules
    }
    # google-beta is implicitly included by cloud-armor/google
  }

  required_version = "~> 1.5"
}

provider "google" {
  project = var.project_id
  region  = var.region
}

#data "google_client_config" "default" {}
