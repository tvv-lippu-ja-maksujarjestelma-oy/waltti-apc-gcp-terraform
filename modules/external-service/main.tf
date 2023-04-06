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
  account_id   = "${var.service_name}"
  display_name = "Terraform Service Account for ${var.service_name}"
}

resource "google_service_account_iam_member" "this_service" {
  service_account_id = google_service_account.this_service.name
  role               = "roles/editor" # TODO: This is overkill
  member             = "serviceAccount:${google_service_account.this_service.email}"
}

resource "google_storage_bucket_iam_member" "this_service" {
  bucket = google_storage_bucket.service_state.name
  role   = "roles/storage.admin"
  member = "serviceAccount:${google_service_account.this_service.email}"
}
