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

#  Normal buckets here!

