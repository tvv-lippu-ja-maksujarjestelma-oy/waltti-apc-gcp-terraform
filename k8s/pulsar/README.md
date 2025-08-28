# Apache Pulsar

Apache Pulsar deployment manifests.

## Overview

The chart is meant for production deployments even though it is not safe for production out of the box.

- Defaults (`./base/apache-pulsar-helm-values.yaml`)
  - Use SSDs
    - As recommended by Apache Pulsar documentation
  - Disable monitoring stack
    - Google Cloud Monitoring + GKE Autopilot is in use
  - Ensure `Service`s use internal Google Cloud networking component variants
    - This deployment is not meant to be exposed publicly outside of the cluster
- Development (`./overlays/dev/values.yaml`)
  - Disables persistence, at least during infra development
    - This way PVCs do not have to be managed
    - **Data will not be persisted in development**

## Requirements

- Kustomize 5.x ([bundled with kubectl 1.14+](https://kubernetes.io/docs/tasks/tools/#kubectl))
- [Helm 3.x](https://helm.sh/docs/intro/install/) available in `$PATH` as `helm`

## Usage

### Render manifests

This will also pull the chart to `./base/charts` if it did not exist.

```sh
# Navigate to environment overlay directory
cd overlays/dev
# Render the resulting manifest
kubectl kustomize --enable-helm
```

### Deploy

Remember to set your kube context appropriately.

```sh
# Activate the correct kube context
kubectl config use-context my-dev-cluster-context
# Navigate to matching environment overlay directory
cd overlays/dev
# Render the manifest and apply it
kubectl kustomize --enable-helm | kubectl apply -f -
```

## References

- [apache/pulsar-helm-chart](https://github.com/apache/pulsar-helm-chart/tree/master)
- [HelmChartInflationGenerator](https://kubectl.docs.kubernetes.io/references/kustomize/builtins/#_helmchartinflationgenerator_)
- [Kustomization Helm example](https://github.com/kubernetes-sigs/kustomize/blob/master/examples/chart.md)
- [Declarative Management of Kubernetes Objects Using Kustomize (kubernetes.io)](https://kubernetes.io/docs/tasks/manage-kubernetes-objects/kustomization/)
