terraform {
  backend "gcs" {
    bucket = "waltti-apc-sandbox-tfstate"
    prefix = "terraform/state"
  }
}