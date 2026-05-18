locals {
  pulsar_tenant = "apc-staging"
  # 14 days in minutes
  retention_minutes = 20160
  # 10 GB in bytes — backlog cap per main namespace.
  # When exceeded, producers get an exception (blocked) rather than messages
  # being silently dropped. Protects against stalled consumers filling bookies.
  backlog_limit_bytes = "10737418240"
}

resource "pulsar_namespace" "source" {
  tenant    = local.pulsar_tenant
  namespace = "source"

  retention_policies {
    retention_minutes    = local.retention_minutes
    retention_size_in_mb = -1
  }

  backlog_quota {
    type          = "destination_storage"
    limit_bytes   = local.backlog_limit_bytes
    limit_seconds = "-1"
    policy        = "producer_exception"
  }
}

resource "pulsar_namespace" "deduplicated" {
  tenant    = local.pulsar_tenant
  namespace = "deduplicated"

  retention_policies {
    retention_minutes    = local.retention_minutes
    retention_size_in_mb = -1
  }

  backlog_quota {
    type          = "destination_storage"
    limit_bytes   = local.backlog_limit_bytes
    limit_seconds = "-1"
    policy        = "producer_exception"
  }
}

resource "pulsar_namespace" "anonymized" {
  tenant    = local.pulsar_tenant
  namespace = "anonymized"

  retention_policies {
    retention_minutes    = local.retention_minutes
    retention_size_in_mb = -1
  }

  backlog_quota {
    type          = "destination_storage"
    limit_bytes   = local.backlog_limit_bytes
    limit_seconds = "-1"
    policy        = "producer_exception"
  }
}

resource "pulsar_namespace" "aggregated" {
  tenant    = local.pulsar_tenant
  namespace = "aggregated"

  retention_policies {
    retention_minutes    = local.retention_minutes
    retention_size_in_mb = -1
  }

  backlog_quota {
    type          = "destination_storage"
    limit_bytes   = local.backlog_limit_bytes
    limit_seconds = "-1"
    policy        = "producer_exception"
  }
}

resource "pulsar_namespace" "cleaned" {
  tenant    = local.pulsar_tenant
  namespace = "cleaned"

  retention_policies {
    retention_minutes    = local.retention_minutes
    retention_size_in_mb = -1
  }

  backlog_quota {
    type          = "destination_storage"
    limit_bytes   = local.backlog_limit_bytes
    limit_seconds = "-1"
    policy        = "producer_exception"
  }
}

resource "pulsar_namespace" "profiles" {
  tenant    = local.pulsar_tenant
  namespace = "profiles"

  retention_policies {
    retention_minutes    = -1
    retention_size_in_mb = 100
  }
}
