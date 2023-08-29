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
