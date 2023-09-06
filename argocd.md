# ArgoCD


## Installation

Directory k8s/argocd contains installation files. Running kubectl apply -f in this directory installs ArgoCD into the cluster. Note taht argocd-patch.yaml adds ksops tool. Also we annotate GCP service accounts so ArgoCD can decode sops secrets ( The installation is based on https://dev.to/stack-labs/gitops-demo-with-argo-cd-and-ksops-on-gke-2a0l ). The GCP terraform code uses ip restrictions for accessing ArgoCD web interface.

### KSOPS 

Added   ```kustomize.buildOptions: --enable-alpha-plugins --enable-exec``` to ArgoCD configmap.

### Cilium

Cilium endpoint causes ArgoCD to have some issues (https://github.com/argoproj/argo-cd/issues/10456). Implemented CM exclusion in the Github message. Solved

## Upgrading

Use ArgoCD upgrade guide for upgrading.

## Applications

Applications that ArgoCD controls are setup via yaml files in k8s/argocd-settings. 


## Adding a new environment 

When adding a new cluster (environemnt):

1. Add dev cluster outbound ip into allowed GKE control plane
2. Add new cluster kubernetes context in ArgoCd cluster via ```argocd cluster add_your_k8s_context_name```

