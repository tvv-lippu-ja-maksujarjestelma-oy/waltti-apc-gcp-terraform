module "cluster" {
  source           = "../../modules/kubernetes"
  environment      = var.environment
  network_name     = module.network.network_name
  management_cidrs = var.management_cidrs
  project_id       = var.project_id
  cluster_name     = var.environment
  k8s_version      = "1.27.3-gke.100"
}
