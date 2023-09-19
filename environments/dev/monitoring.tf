# Mismatch in k8s namespace (dev) and actual env (created as sandbox)
# Note this terraform module/GCP has issues, might have to run multiple times to create them all
module "anonymizer" {
  source          = "../../modules/monitor-service"
  service_id      = "anonymizer"
  controller_name = "anonymizer"
  cluster_name    = "prototype"
  environment     = "dev"
  region          = var.region
  project_id      = var.project_id
}

module "gtfsrt_vp_poller_kuopio" {
  source          = "../../modules/monitor-service"
  service_id      = "gtfsrt-vp-poller-kuopio"
  controller_name = "gtfsrt-vp-poller-fi-kuopio"
  cluster_name    = "prototype"
  environment     = "dev"
  region          = var.region
  project_id      = var.project_id
}

module "gtfsrt_vp_poller_jyvaskyla" {
  source          = "../../modules/monitor-service"
  service_id      = "gtfsrt-vp-poller-jyvaskyla"
  controller_name = "gtfsrt-vp-poller-fi-jyvaskyla"
  cluster_name    = "prototype"
  environment     = "dev"
  region          = var.region
  project_id      = var.project_id
}

module "journey_matcher" {
  source          = "../../modules/monitor-service"
  service_id      = "journey-matcher"
  controller_name = "journey-matcher"
  cluster_name    = "prototype"
  environment     = "dev"
  region          = var.region
  project_id      = var.project_id
}

module "vehicle-position-splitter" {
  source          = "../../modules/monitor-service"
  service_id      = "vehicle-position-splitter"
  controller_name = "vehicle-position-splitter"
  cluster_name    = "prototype"
  environment     = "dev"
  region          = var.region
  project_id      = var.project_id
}

module "mqtt_deduplicator" {
  source          = "../../modules/monitor-service"
  service_id      = "mqtt-deduplicator"
  controller_name = "mqtt-deduplicator"
  cluster_name    = "prototype"
  environment     = "dev"
  region          = var.region
  project_id      = var.project_id
}

module "mqtt_pulsar_forwarder" {
  source          = "../../modules/monitor-service"
  service_id      = "mqtt-pulsar-forwarder"
  controller_name = "mqtt-pulsar-forwarder"
  cluster_name    = "prototype"
  environment     = "dev"
  region          = var.region
  project_id      = var.project_id
}

module "pulsar_mqtt_forwarder_raportointi" {
  source          = "../../modules/monitor-service"
  service_id      = "pulsar-mqtt-forwarder-raportointi"
  controller_name = "pulsar-mqtt-forwarder-raportointi"
  cluster_name    = "prototype"
  environment     = "dev"
  region          = var.region
  project_id      = var.project_id
}

module "pulsar_mqtt_forwarder_rtpi" {
  source          = "../../modules/monitor-service"
  service_id      = "pulsar-mqtt-forwarder-rtpi"
  controller_name = "pulsar-mqtt-forwarder-rtpi"
  cluster_name    = "prototype"
  environment     = "dev"
  region          = var.region
  project_id      = var.project_id
}

module "vehicle_registry_monitor_kuopio" {
  source          = "../../modules/monitor-service"
  service_id      = "vehicle-registy-kuopio"
  controller_name = "vehicle-registy-poller-fi-kuopio"
  cluster_name    = "prototype"
  environment     = "dev"
  region          = var.region
  project_id      = var.project_id
}
