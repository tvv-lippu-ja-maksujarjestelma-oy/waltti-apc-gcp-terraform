module "argocd" {
  source     = "../../modules/argocd"
  project_id = var.project_id
}
