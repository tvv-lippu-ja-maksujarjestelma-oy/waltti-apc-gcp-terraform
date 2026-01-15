variable "region" {
  default = "europe-west3"
}

variable "environment" {
}

variable "enable_nat" {
  description = "Enable Cloud NAT"
  type        = bool
  default     = true
}