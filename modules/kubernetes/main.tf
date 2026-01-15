locals {
  cluster_name           = google_container_cluster.primary.name
  cluster_endpoint       = google_container_cluster.primary.endpoint
  cluster_ca_certificate = google_container_cluster.primary.master_auth.0.cluster_ca_certificate
}

data "google_project" "current" {}

resource "google_service_account" "gke" {
  account_id   = "cluster-serviceaccount"
  display_name = "Service Account for GKE"
}

resource "google_project_iam_member" "gke_policy" {
  project = var.project_id
  role    = "roles/container.nodeServiceAccount"
  member  = "serviceAccount:${google_service_account.gke.email}"
}

resource "google_project_iam_member" "gke_log_writer" {
  project = var.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${google_service_account.gke.email}"
}

resource "google_project_iam_member" "gke_metric_writer" {
  project = var.project_id
  role    = "roles/monitoring.metricWriter"
  member  = "serviceAccount:${google_service_account.gke.email}"
}

resource "google_project_iam_member" "gke_monitoring_viewer" {
  project = var.project_id
  role    = "roles/monitoring.viewer"
  member  = "serviceAccount:${google_service_account.gke.email}"
}

resource "google_project_iam_member" "gke_stackdriver_writer" {
  project = var.project_id
  role    = "roles/stackdriver.resourceMetadata.writer"
  member  = "serviceAccount:${google_service_account.gke.email}"
}

resource "google_service_account_iam_member" "gke_robot_sa_user" {
  service_account_id = google_service_account.gke.name
  role               = "roles/iam.serviceAccountUser"
  member             = "serviceAccount:service-${data.google_project.current.number}@container-engine-robot.iam.gserviceaccount.com"
}

resource "google_container_cluster" "primary" {

  name     = var.cluster_name
  location = var.region
  deletion_protection = false

  enable_autopilot = true
  # GKE autopilot are by default in regular channel
  # See https://cloud.google.com/kubernetes-engine/docs/concepts/release-channels
  min_master_version = var.k8s_version

  network    = "network"
  subnetwork = "${var.environment}-gke"

  ip_allocation_policy {
    cluster_secondary_range_name  = "gke-pods"
    services_secondary_range_name = "gke-services"
  }

  vertical_pod_autoscaling {
    enabled = true
  }

  master_authorized_networks_config {

    dynamic "cidr_blocks" {
      for_each = var.management_cidrs
      content {
        cidr_block = cidr_blocks.value
      }

    }
  }

  dynamic "control_plane_endpoints_config" {
    # Conditionally enabled. Only one block per resource.
    for_each = var.dns_endpoint_enabled == true ? toset([true]) : toset([])
    content {
      dns_endpoint_config {
        allow_external_traffic = var.dns_endpoint_enabled
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

  monitoring_config {
    enable_components = ["SYSTEM_COMPONENTS"]

    managed_prometheus {
      enabled = true
    }
  }

  cluster_autoscaling {
    auto_provisioning_defaults {
      service_account = google_service_account.gke.email
    }
  }

}

