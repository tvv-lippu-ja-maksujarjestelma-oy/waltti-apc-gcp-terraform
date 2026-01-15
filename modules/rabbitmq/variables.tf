variable "region" {
  default = "europe-west3"
}

variable "project_id" {
  default = "Project_ID"
}

variable "dns_service_account_id" {
}

variable "create_iam_binding" {
  description = "Create IAM binding for cert-manager"
  type        = bool
  default     = true
}
