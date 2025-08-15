module "rabbitmq" {
  source     = "../../modules/rabbitmq"
  region     = var.region
  project_id = var.project_id
}
