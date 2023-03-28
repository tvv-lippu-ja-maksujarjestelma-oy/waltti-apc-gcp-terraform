# Storing a non gcp based service's backend+state files
resource "google_storage_bucket" "cloudamqp-tf-state" {
  name                        = "waltti-cloudamqp-${var.environment}-tfstate"
  location                    = var.region
  storage_class               = "STANDARD"
  uniform_bucket_level_access = true
  versioning {
    enabled = true
  }
}

resource "google_storage_bucket" "streamnative-tf-state" {
  name                        = "waltti-streamnative-${var.environment}-tfstate"
  location                    = var.region
  storage_class               = "STANDARD"
  uniform_bucket_level_access = true
  versioning {
    enabled = true
  }
}

resource "google_service_account" "cloudamqp" {
  account_id   = "cloudamqp"
  display_name = "Terraform Service Account for cloudamqp"
}

resource "google_service_account_iam_member" "cloudamqp" {
  service_account_id = google_service_account.cloudamqp.name
  role               = "roles/editor" # Overkill
  member             = "serviceAccount:${google_service_account.cloudamqp.email}"
}

resource "google_storage_bucket_iam_member" "cloudamqp" {
  bucket = google_storage_bucket.cloudamqp-tf-state.name
  role   = "roles/storage.admin"
  member = "serviceAccount:${google_service_account.cloudamqp.email}"
}

resource "google_service_account" "streamnative" {
  account_id   = "streamnative-serviceaccount"
  display_name = "Service Account for streamnative"
}

resource "google_service_account_iam_member" "streamnative" {
  service_account_id = google_service_account.streamnative.name
  role               = "roles/editor" # TODO: This is overkill
  member             = "serviceAccount:${google_service_account.streamnative.email}"
}

resource "google_storage_bucket_iam_member" "streamnative" {
  bucket = google_storage_bucket.streamnative-tf-state.name
  role   = "roles/storage.admin"
  member = "serviceAccount:${google_service_account.streamnative.email}"
}

output "cloudamqp-tf-state-bucket" {
  value = google_storage_bucket.cloudamqp-tf-state.name
}

output "streamnative-tf-state-bucket" {
  value = google_storage_bucket.streamnative-tf-state.name
}