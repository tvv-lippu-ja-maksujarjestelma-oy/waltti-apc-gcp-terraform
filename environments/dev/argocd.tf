# SA for Argocd
resource "google_service_account" "argocd_gke" {
  account_id   = "argocd-gke"
  display_name = "ArgoCD service account"
}

resource "google_service_account_iam_member" "argocd_gke" {
  service_account_id = google_service_account.argocd_gke.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "serviceAccount:${var.project_id}.svc.id.goog[argocd/argocd-gke]" # k8s namespace/sa
}

resource "google_project_iam_member" "argocd_gke" {
  project = var.project_id
  role    = "roles/cloudkms.cryptoKeyEncrypterDecrypter"
  member  = "serviceAccount:${google_service_account.argocd_gke.email}"
}


# kubectl 1. create ns,  2. install argo, 3. patch argo (ksops) 4. annotate sa 5. install project, repo, app(s)
