resource "google_compute_network" "vpc" {
  name = "network"

  routing_mode = "REGIONAL"

  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "gke" {
  name = "${var.environment}-gke"
  # TODO: CIDR ranges needs to be different in different envs?
  ip_cidr_range = "10.0.0.0/20" # 10.0.0.0 - 10.0.15.255, 4094
  region        = var.region
  network       = google_compute_network.vpc.id

  purpose                  = "PRIVATE"
  private_ip_google_access = true

  secondary_ip_range {
    range_name    = "gke-services"
    ip_cidr_range = "10.0.16.0/22" # 10.0.16.0 - 10.0.19.255, 1022
  }
  secondary_ip_range {
    range_name    = "gke-pods"
    ip_cidr_range = "10.0.128.0/17" # 10.0.128.0 - 10.0.255.255, 32766
  }
}

resource "google_compute_router" "router" {
  name    = "nat-router"
  network = google_compute_network.vpc.name
  region  = var.region
}

resource "google_compute_router_nat" "nat" {
  name                               = "nat-router"
  router                             = google_compute_router.router.name
  region                             = var.region
  nat_ip_allocate_option             = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"

  log_config {
    enable = true
    filter = "ERRORS_ONLY"
  }
}