module "cloudamqp" {
  source                         = "../../modules/external-service"
  service_name                   = "cloudamqp"
  allow_service_account_creation = true
  environment                    = var.environment
  region                         = var.region
  project_id                     = var.project_id
}

module "mqtt" {
  source             = "../../modules/external-service"
  service_name       = "mqtt-setup"
  secret_name_starts = "mqtt"
  environment        = var.environment
  region             = var.region
  project_id         = var.project_id
}

module "streamnative" {
  source       = "../../modules/external-service"
  service_name = "streamnative"
  environment  = var.environment
  region       = var.region
  project_id   = var.project_id

}
