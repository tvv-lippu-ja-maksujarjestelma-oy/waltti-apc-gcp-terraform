# Terraform setup

## Initial terraform setup 
1. Select GCP project
```gcloud config create foo / gcloud init ```
2. Create a service account
```gcloud iam service-accounts create terraform  --display-name "Terraform account"```

3. Give the service account some rights
```gcloud projects add-iam-policy-binding PROJECT_ID --member=serviceAccount:terraform@PROJECT_ID.iam.gserviceaccount.com --role=roles/editor`

## Kubernes setup

k8s contains raw yaml files for installing:
- ArgoCD
- RabbitMQ
- Cert-Manager

### Cert-Manager
Cert-manager tries by default to create resources in the kube-system namespace, which is not possible in GKE autopilot. All mentions of kube-system are replaced with cert-manager namespace.

Also to use the DNS solver for an issuer, you need to link the cert-manager service account to the GCP service account with the permissions to modify DNS records. DNS management is done in the apc-sandbox project:

```shell
kubectl annotate serviceaccount --namespace=cert-manager cert-manager \
    "iam.gke.io/gcp-service-account=cert-manager-dns@apc-sandbox.iam.gserviceaccount.com"
```

### RabbitMQ

More information at [RABBITMQ.MD](./RABBITMQ.MD)

## Modules

Directory modules contains two terraform modules

### kubernetes module

A basic GCP autopilot cluster

### network module

A basic GCP network

## Tests

Contains basic tests etc
