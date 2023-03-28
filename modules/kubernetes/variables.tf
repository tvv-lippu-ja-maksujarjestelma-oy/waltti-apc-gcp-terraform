variable "region" {
  default = "europe-west3"
}

variable "environment" {
}

variable "management_cidrs" {
  type = list(string)
}

variable "network_name" {
  
}