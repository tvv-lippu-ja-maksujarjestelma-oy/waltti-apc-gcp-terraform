output "argocd_global_ip" {
  value = google_compute_global_address.argocd.address
}