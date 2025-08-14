resource "google_compute_global_address" "rabbitmq" {
  name = "rabbitmq"
}

resource "google_compute_global_address" "rabbitmq-ui" {
  name = "rabbitmq-ui"
}
