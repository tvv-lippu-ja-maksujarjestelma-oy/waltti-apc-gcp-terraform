variable "environment" {
}

variable "region" {
  default = "europe-west3"
}

variable "project_id" {
  default = "Project_ID"
}

variable "secret_name_starts" {
  type    = string
  default = null
}

variable "service_name" {
  type = string
}

variable "allow_service_account_creation" {
  type = bool
  default = false
}
