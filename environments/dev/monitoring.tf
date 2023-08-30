module "gtfsrt_vp_poller_kuopio" {
  source          = "../../modules/monitor-service"
  service_id      = "gtfsrt-vp-poller-kuopio"
  controller_name = "gtfsrt-vp-poller-fi-kuopio"
  cluster_name    = "prototype"
  environment     = var.environment
  region          = var.region
  project_id      = var.project_id
}

module "gtfsrt_vp_poller_jyvaskyla" {
  source          = "../../modules/monitor-service"
  service_id      = "gtfsrt-vp-poller-jyvaskyla"
  controller_name = "gtfsrt-vp-poller-fi-jyvaskyla"
  cluster_name    = "prototype"
  environment     = var.environment
  region          = var.region
  project_id      = var.project_id
}

module "vehicle_registry_monitor_kuopio" {
  source          = "../../modules/monitor-service"
  service_id      = "vehicle-registy-kuopio"
  controller_name = "vehicle-registy-poller-fi-kuopio"
  cluster_name    = "prototype"
  environment     = var.environment
  region          = var.region
  project_id      = var.project_id
}
