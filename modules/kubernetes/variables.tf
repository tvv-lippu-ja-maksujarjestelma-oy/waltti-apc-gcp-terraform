variable "region" {
  default = "europe-west3"
}

variable "project_id" {
  default = "Project_ID"
}

variable "environment" {
}

variable "management_cidrs" {
  type = list(string)
}

variable "network_name" {

}

variable "cluster_name" {
  type    = string
  default = "prototype"

}

variable "k8s_version" {
  type    = string
  default = "1.25.8-gke.500"
}

variable "dns_endpoint_enabled" {
  type        = bool
  default     = null # Backwards-compatible default
  description = <<-DESC
    Enable public-facing DNS endpoint for the GKE cluster?

    See:

    - https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/container_cluster#allow_external_traffic-1
    - https://cloud.google.com/blog/products/containers-kubernetes/new-dns-based-endpoint-for-the-gke-control-plane
    - https://cloud.google.com/kubernetes-engine/docs/how-to/latest/network-isolation#dns-based-endpoint
  DESC
}
