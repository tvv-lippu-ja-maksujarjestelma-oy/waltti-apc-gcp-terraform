terraform {
  required_providers {
    google = {
      source = "hashicorp/google"
      # Provider version is resolved from used modules
    }
    pulsar = {
      source  = "registry.terraform.io/streamnative/pulsar"
      version = "~> 0.7.0"
    }
  }

  required_version = "~> 1.5"
}

provider "google" {
  project = var.project_id
  region  = var.region
}

#data "google_client_config" "default" {}

# Pulsar admin API via internal LoadBalancer service (pulsar-broker-admin).
# Only reachable from within the GCP VPC / management network.
# For local use without port-forward, run 'kubectl proxy --port=8001' and set:
#   TF_VAR_pulsar_web_service_url=http://localhost:8001/api/v1/namespaces/pulsar/services/pulsar-broker-admin:8080/proxy
provider "pulsar" {
  web_service_url = var.pulsar_web_service_url
}
