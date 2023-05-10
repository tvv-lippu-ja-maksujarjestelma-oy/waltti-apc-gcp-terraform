# External service

Contains a simple bucket+service account for external service terraform state management

## secret_name_starts

Sets the GCP service account to read the secret. The variable also sets the secret's name conditional

Ie. if the variable is foo, secret must start with foo