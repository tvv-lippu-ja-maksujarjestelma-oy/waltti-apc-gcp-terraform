# IP for mqtt
output "rabbitmq_ip" {
  value = google_compute_address.rabbitmq.address
}

# IP for management UI
output "rabbitmq_ui_global_ip" {
  value = google_compute_global_address.rabbitmq-ui.address
}
