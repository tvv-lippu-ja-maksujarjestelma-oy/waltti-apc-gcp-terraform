# October 2026 resource sizing

`nonproduction.json` is the resource-only patch bundle deployed on 15 October.
`production.json` is the corresponding production bundle, not deployed today.
Most application requests are already 50m/256Mi in nonproduction and remain there.
Retain MQTT ingestion anti-affinity, replicas, CPU/memory limits and Pulsar disks.

The observer captures readiness, pod restarts/OOMs, certificate status, container
CPU/memory metrics, failed batch jobs and Pulsar topic/subscription counters every
five minutes. Reader subscriptions retain pre-existing historical backlogs and are
excluded from the pipeline backlog check. The gate requires a complete 24-hour
window, no unhealthy samples and no gap exceeding 15 minutes. It fails closed on
missing credentials or missing telemetry. The local Mac must stay awake, online,
and able to reach GKE; launchd does not provide a hosted monitoring guarantee.

Runtime files live in `/Users/ilkka/Waltti/analysis/sizing-campaign-20261015`.
`status.json` exposes observation progress and the earliest production time.
`production-preflight.json` and `production-result.json` record tomorrow's outcome.
The local launchd entry point is `tick.py`; it stops after a terminal outcome.
It does not post Slack or email messages.

Production promotion checks frozen PR heads, CI status, unchanged production
images, unchanged default branches, healthy/synced Argo applications, readiness and inactive GKE operations.
Existing Argo drift blocks the entire promotion, requiring review rather than
silently deploying another image. Before merging the approved PRs it temporarily
disables automated sync on the parent and affected applications and applies only resource fields,
sequentially. Every rollout must finish and pass health checks. On failure it
restores prior resource fields and leaves automated sync disabled until merged
source is reconciled. An interrupted attempt is never retried automatically.

Run `python3 -m unittest discover -s operations/sizing-2026-10-15 -p test_observe.py`
for time/coverage/error/PR-head/rollback guards. `promote.py --preflight-only` is
read-only and never merges or changes a workload. `observe.py --arm` establishes
the immutable healthy baseline; do this only after rollouts and batch checks pass.

Self-signed certificate smoke tests exercise issuance/admission but do not exercise
external ACME DNS challenges. Pulsar init smoke tests run read-only cluster-ID
queries at the new CPU request before rolling StatefulSets.

Dev has three pre-existing irrecoverable ledgers (150, 151, 153), confirmed in
Cloud Logging entries before the resize began. `known-underreplication.json`
records that exact exception; every new under-replicated ledger blocks promotion.
Staging and production have no allowed under-replication exceptions. Every sample
also requires four writable bookies, an elected auditor and enabled replication.
No ledger or persistent data is deleted by this campaign.


## Approved supervised rollout on 16 October

The initial overnight observation did not pass: coverage gaps, node maintenance,
planned dev image updates and pre-existing crashes are retained in the evidence.
After reviewing those findings the user explicitly approved today's supervised
production rollout, excluding all three vehicle-position splitters. Their existing
250m/512Mi requests and images stay unchanged.

`--supervised-approved` requires the approval record to match the exact 18-target
patch bundle hash. It bypasses only the failed 24-hour time/coverage gate; current
health, PR heads/checks, reviewed main heads and production images remain guarded.
The old automatic-promotion launch agent is unloaded before this mode runs.
Pulsar rolls one ordinal at a time using a temporary StatefulSet partition,
checking writable bookies, replication and message flow before moving on. The
original update strategy is restored afterwards. Image digests are verified, and
15 minutes of health observation precedes restoration of automatic Argo sync.
