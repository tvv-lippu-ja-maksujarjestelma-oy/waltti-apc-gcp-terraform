terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.64.0"

    }
  }

  required_version = "~> 1.3"
}

provider "google" {
  project = var.project_id
  region  = var.region
}
