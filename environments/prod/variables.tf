variable "project_id" {
  default = "Project_ID"
}

variable "region" {
  default = "europe-west3"
}

variable "tf_service_account" {
  sensitive = true
}

variable "argocd_service_account" {
  sensitive = true
}

variable "environment" {
}

variable "management_cidrs" {
}

variable "maintenance_start_time" {
  default = "00:30"
}

variable "maintenance_end_time" {
  default = "05:00"
}

variable "maintenance_recurrence" {
  default = "FREQ=WEEKLY"
}

variable "gcp_service_list" {
  type    = list(string)
  default = ["compute.googleapis.com", "cloudkms.googleapis.com", "container.googleapis.com", "secretmanager.googleapis.com", "cloudresourcemanager.googleapis.com"]
}

variable "dns_service_account_id" {
  sensitive = true
}
variable "pulsar_web_service_url" {
  description = "Pulsar broker admin API URL. Defaults to internal LB. For local use: run kubectl proxy --port=8001 and set TF_VAR_pulsar_web_service_url=http://localhost:8001/api/v1/namespaces/pulsar/services/pulsar-broker-admin:8080/proxy"
  default     = "http://10.0.0.35:8080"
}
