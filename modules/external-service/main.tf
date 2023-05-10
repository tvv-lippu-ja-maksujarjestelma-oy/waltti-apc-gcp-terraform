data "google_project" "project" {}

locals {
  create_secret_reader = var.secret_name_starts != null
  project_number       = data.google_project.project.number
}

# Storing a non gcp based service's backend+state files
resource "google_storage_bucket" "service_state" {
  name                        = "waltti-${var.service_name}-${var.environment}-tfstate"
  location                    = var.region
  storage_class               = "STANDARD"
  uniform_bucket_level_access = true
  public_access_prevention    = "enforced"
  versioning {
    enabled = true
  }
}

resource "google_service_account" "this_service" {
  account_id   = var.service_name
  display_name = "Terraform Service Account for ${var.service_name}"
}

resource "google_storage_bucket_iam_member" "this_service" {
  bucket = google_storage_bucket.service_state.name
  role   = "roles/storage.admin"
  member = "serviceAccount:${google_service_account.this_service.email}"
}

resource "google_project_iam_member" "secret_meta_viewer" {
  count   = local.create_secret_reader ? 1 : 0
  project = var.project_id
  role    = "roles/secretmanager.viewer"
  member  = "serviceAccount:${google_service_account.this_service.email}"

}

resource "google_project_iam_member" "secret_accessor" {
  count   = local.create_secret_reader ? 1 : 0
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.this_service.email}"

  condition {
    title       = "access secrets"
    description = "Allow to read related secrets"
    expression  = "resource.name.startsWith('projects/${local.project_number}/secrets/${var.secret_name_starts}-')"

  }
}