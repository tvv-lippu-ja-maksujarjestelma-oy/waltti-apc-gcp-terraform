output "cluster_name" {
  value = local.cluster_name
}

output "endpoint" {
  sensitive = true
  description = "Cluster endpoint"
  value = local.cluster_endpoint
  depends_on = [
    google_container_cluster.primary
  ]
}

output "ca_certificate" {
  sensitive = true
  description = "Cluster ca cert (base64 encoded)"
  value = local.cluster_ca_certificate
}