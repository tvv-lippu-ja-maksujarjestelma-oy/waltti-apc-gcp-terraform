output "rabbitmq_global_ip" {
  value = google_compute_global_address.rabbitmq.address
}

output "rabbitmq_ui_global_ip" {
  value = google_compute_global_address.rabbitmq-ui.address
}
