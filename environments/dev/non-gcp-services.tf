module "cloudamqp" {
  source = "../../modules/external-service"
  service_name = "cloudamqp"
  environment  = var.environment
  region       = var.region
}

module "mqtt" {
  source       = "../../modules/external-service"
  service_name = "mqtt-setup"
  environment  = var.environment
  region       = var.region
}

module "streamnative" {
  source = "../../modules/external-service"
  service_name = "streamnative"
  environment = var.environment
  region = var.region
}
