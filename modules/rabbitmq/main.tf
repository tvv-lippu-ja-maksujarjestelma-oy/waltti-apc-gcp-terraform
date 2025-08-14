resource "google_compute_address" "rabbitmq" {
  name   = "rabbitmq"
  region = var.region
}

resource "google_compute_global_address" "rabbitmq-ui" {
  name = "rabbitmq-ui"
}
