locals {
  repo = "tvv-lippu-ja-maksujarjestelma-oy/waltti-apc-gcp-terraform"
}

# Create a sops+argocd kms key
resource "google_kms_key_ring" "sops" {
  name     = "sops"
  location = "global"
}

resource "google_kms_crypto_key" "sops" {
  # Add a new create to the key ring
  name     = "sops-key"
  key_ring = google_kms_key_ring.sops.id
}

# Github 
resource "google_iam_workload_identity_pool" "github_pool" {
  workload_identity_pool_id = "github-pool"
  display_name              = "GitHub pool"
  description               = "Identity pool for GitHub deployments"
}

resource "google_iam_workload_identity_pool_provider" "github" {
  workload_identity_pool_id          = google_iam_workload_identity_pool.github_pool.workload_identity_pool_id
  workload_identity_pool_provider_id = "github-provider"
  attribute_mapping = {
    "google.subject"       = "assertion.sub"
    "attribute.repository" = "assertion.repository"
  }
  oidc {
    issuer_uri = "https://token.actions.githubusercontent.com"
  }
}

resource "google_service_account_iam_member" "workload_identity_user" {
  service_account_id = "projects/apc-sandbox/serviceAccounts/terraform@apc-sandbox.iam.gserviceaccount.com"
  role               = "roles/iam.workloadIdentityUser"
  member             = "principalSet://iam.googleapis.com/${google_iam_workload_identity_pool.github_pool.name}/attribute.repository/${local.repo}"
}
