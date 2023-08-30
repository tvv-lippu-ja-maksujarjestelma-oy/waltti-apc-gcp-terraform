resource "google_monitoring_service" "this" {
  service_id   = var.service_id
  display_name = var.service_id

  basic_service {
    service_type = "GKE_WORKLOAD"
    service_labels = {
      cluster_name              = var.cluster_name,
      location                  = var.region,
      namespace_name            = var.environment
      project_id                = var.project_id,
      top_level_controller_name = var.controller_name,
      top_level_controller_type = "Deployment"
    }
  }
}

resource "google_monitoring_slo" "this" {
  service             = google_monitoring_service.this.service_id
  display_name        = "${var.controller_name}-restart-count"
  goal                = 0.1
  rolling_period_days = 7

  request_based_sli {
    good_total_ratio {
      good_service_filter = "metric.type=\"kubernetes.io/container/restart_count\" resource.type=\"k8s_container\""
      bad_service_filter  = "metric.type=\"kubernetes.io/container/restart_count\" resource.type=\"k8s_container\""
    }
  }
}

resource "google_monitoring_alert_policy" "this" {
  display_name = "restart-alert"
  combiner     = "OR"
  //notification_channels = "XXX" TODO: implement notification strategy
  alert_strategy {
    auto_close = "604800s"
  }

  conditions {
    display_name = "Burn rate on 50% - Good/Total Ratio - Rolling 7 days"
    condition_threshold {
      filter = "select_slo_burn_rate(\"${google_monitoring_slo.this.name}\", \"3600s\")"

      duration   = "0s"
      comparison = "COMPARISON_GT"
      aggregations {
        alignment_period     = "300s"
        cross_series_reducer = "REDUCE_NONE"
      }
      trigger {
        count = 1
      }
      threshold_value = 10
    }
  }
}