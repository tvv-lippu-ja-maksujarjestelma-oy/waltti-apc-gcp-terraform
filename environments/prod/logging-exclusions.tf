# Image-streaming node logs (gcfsd, gcfs-snapshotter) are GKE-internal: about
# 2.5 GiB a day here (Nov 2026 cost review). Excluding them from the _Default
# sink stops paying for their storage. ERROR and higher are kept for debugging
# image pulls.
resource "google_logging_project_exclusion" "image_streaming_node_logs" {
  project     = "apc-prod-397611"
  name        = "exclude-image-streaming-node-logs"
  description = "GKE image-streaming node logs (gcfsd, gcfs-snapshotter) below ERROR"
  filter      = "resource.type=\"k8s_node\" AND (log_id(\"gcfsd\") OR log_id(\"gcfs-snapshotter\")) AND severity<ERROR"
}

# Created with the Logging API on 17 Nov 2026; the next apply adopts it.
import {
  to = google_logging_project_exclusion.image_streaming_node_logs
  id = "projects/apc-prod-397611/exclusions/exclude-image-streaming-node-logs"
}
