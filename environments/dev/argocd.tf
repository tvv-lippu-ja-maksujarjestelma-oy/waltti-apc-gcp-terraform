module "argocd" {
  source     = "../../modules/argocd"
  project_id = var.project_id
}

module "argo_allowed" {
  source              = "GoogleCloudPlatform/cloud-armor/google"
  project_id          = var.project_id
  name                = "argocd-access"
  description         = "Allow ArgoCD access"
  default_rule_action = "deny(403)"

  security_rules = {
    "allow_accces" = {
      action        = "allow"
      priority      = 11
      src_ip_ranges = var.management_cidrs
    }
  }
}