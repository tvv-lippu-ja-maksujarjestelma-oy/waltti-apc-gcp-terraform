locals {
  cluster_name = google_container_cluster.primary.name
  cluster_endpoint = google_container_cluster.primary.endpoint
  cluster_ca_certificate = google_container_cluster.primary.master_auth.0.cluster_ca_certificate
}

resource "google_service_account" "gke" {
  account_id   = "cluster-serviceaccount"
  display_name = "Service Account for GKE"
}

resource "google_container_cluster" "primary" {

  name     = "prototype"
  location = var.region

  enable_autopilot = true
  #min_master_version = data.google_container_engine_versions.gke.latest_master_version

  network    = "network"
  subnetwork = "sandbox-gke"

  ip_allocation_policy {
    cluster_secondary_range_name  = "gke-pods"
    services_secondary_range_name = "gke-services"
  }

  vertical_pod_autoscaling {
    enabled = true
  }

  master_authorized_networks_config {

    dynamic "cidr_blocks" {
      for_each =  var.management_cidrs
      content {
        cidr_block = cidr_blocks.value
      }
      
    }
  }

  private_cluster_config {
    enable_private_nodes    = true
    enable_private_endpoint = false # Enable access from both private and public endpoints
    master_ipv4_cidr_block  = "172.16.0.0/28"
  }

  release_channel {
    channel = "REGULAR"
  }

  # maintenance_policy {
  #   # You must allow at least 48 hours of maintenance availability in a 32-day rolling window.
  #   # Only contiguous availability windows of at least four hours are considered.
  #   recurring_window {
  #     start_time = var.maintenance_start_time
  #     end_time   = var.maintenance_end_time
  #     recurrence = var.maintenance_recurrence
  #   }
  # }

  # notification_config {
  #   pubsub {
  #     enabled = true
  #     topic   = google_pubsub_topic.gke-notifications.id
  #   }
  # }

  # monitoring_config {
  #   enable_components = ["SYSTEM_COMPONENTS"]

  #   managed_prometheus {
  #     enabled = true
  #   }
  # }

  cluster_autoscaling {
    auto_provisioning_defaults {
      service_account = google_service_account.gke.email
    }
  }

}