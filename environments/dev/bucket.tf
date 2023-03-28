# Terraform state bucket
resource "google_storage_bucket" "gcp-tf-state" {
  name          = "waltti-apc-${var.environment}-tfstate"
  location      = var.region
  storage_class = "STANDARD"
  versioning {
    enabled = true
  }
}

#  Normal buckets here!

# Outputs
output "gcp-tf-state-bucket" {
  value = google_storage_bucket.gcp-tf-state.name
}

