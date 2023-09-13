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
  default = ["compute.googleapis.com", "cloudkms.googleapis.com", "container.googleapis.com", "secretmanager.googleapis.com"]

}