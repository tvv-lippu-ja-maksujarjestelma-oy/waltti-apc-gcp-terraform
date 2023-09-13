terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.82.0"

    }
  }

  required_version = "~> 1.5"
}

provider "google" {
  project = var.project_id
  region  = var.region
}

#data "google_client_config" "default" {}
