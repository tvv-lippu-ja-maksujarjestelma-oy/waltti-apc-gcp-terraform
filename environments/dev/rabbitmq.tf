module "rabbitmq" {
  source                 = "../../modules/rabbitmq"
  region                 = var.region
  project_id             = var.project_id
  dns_service_account_id = module.cert-manager.dns_service_account_id
}
