# Cloud Sink test here
resource "google_storage_bucket" "pulsar_cloud_sink" {
  name                        = "apc-pulsar-${var.environment}-sink"
  location                    = var.region
  storage_class               = "STANDARD"
  uniform_bucket_level_access = true
  public_access_prevention    = "enforced"
}

resource "google_service_account" "pulsar_sink" {
  account_id   = "pulsar-sink"
  display_name = "pulsar-sink"
  description = "Pulsar data bucket sink"
}

resource "google_storage_bucket_iam_member" "this_service" {
  bucket = google_storage_bucket.pulsar_cloud_sink.name
  role   = "roles/storage.admin"
  member = "serviceAccount:${google_service_account.pulsar_sink.email}"
}
