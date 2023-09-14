terraform {
  backend "gcs" {
    bucket = "waltti-apc-prod-tfstate"
    prefix = "terraform/state"
  }
}