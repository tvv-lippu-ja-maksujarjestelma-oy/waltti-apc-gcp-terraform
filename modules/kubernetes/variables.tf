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