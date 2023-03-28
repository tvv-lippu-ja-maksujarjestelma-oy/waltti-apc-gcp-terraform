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

