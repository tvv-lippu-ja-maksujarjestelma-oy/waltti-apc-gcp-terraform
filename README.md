# Terraform setup

## Initial terraform setup 
1. Select GCP project
```gcloud config create foo / gcloud init ```
2. Create a service account
```gcloud iam service-accounts create terraform  --display-name "Terraform account"```

3. Give the service account some rights
```gcloud projects add-iam-policy-binding PROJECT_ID --member=serviceAccount:terraform@PROJECT_ID.iam.gserviceaccount.com --role=roles/editor`

## Kubernes setup

k8s contains raw yaml files for installing ArgoCD


## Modules

Directory modules contains two terraform modules

### kubernetes module

A basic GCP autopilot cluster

### network module

A basic GCP network

## Tests

Contains basic tests etc