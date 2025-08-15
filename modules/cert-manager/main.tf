resource "google_service_account" "cert_manager_dns" {
  account_id   = "cert-manager-dns"
  display_name = "Cert-manager DNS challenge solver service account"
}

# TODO: apply only necessary permissions
resource "google_project_iam_member" "cert_manager_dns_admin" {
  project = var.project_id
  role    = "roles/dns.admin"
  member  = "serviceAccount:${google_service_account.cert_manager_dns.email}"
}
