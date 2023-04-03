# Terraform state bucket
resource "google_storage_bucket" "gcp-tf-state" {
  name                        = "waltti-apc-${var.environment}-tfstate"
  location                    = var.region
  storage_class               = "STANDARD"
  uniform_bucket_level_access = true
  public_access_prevention    = "enforced"
  versioning {
    enabled = true
  }
}

# TODO: Terraform SA needs access to bucket
# resource "google_storage_bucket_iam_member" "cloudamqp" {
#   bucket = google_storage_bucket.gcp-tf-state.name
#   role   = "roles/storage.admin"
#   member = "serviceAccount:XXXX
# }

#  Normal buckets here!
