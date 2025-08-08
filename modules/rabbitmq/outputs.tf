output "rabbitmq_global_ip" {
  value = google_compute_global_address.rabbitmq.address
}
