resource "google_compute_address" "rabbitmq" {
  name   = "rabbitmq"
  region = var.region
}

resource "google_compute_global_address" "rabbitmq-ui" {
  name = "rabbitmq-ui"
}

resource "google_service_account_iam_member" "cert_manager_dns_workload" {
  service_account_id = var.dns_service_account_id
  role               = "roles/iam.workloadIdentityUser"
  member             = "serviceAccount:${var.project_id}.svc.id.goog[cert-manager/cert-manager]"
}
