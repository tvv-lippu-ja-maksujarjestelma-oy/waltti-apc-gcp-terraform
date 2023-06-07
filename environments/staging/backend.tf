terraform {
  backend "gcs" {
    bucket = "waltti-apc-staging-tfstate"
    prefix = "terraform/state"
  }
}