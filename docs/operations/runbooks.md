# Operational runbook specifications

Version: 0.6 | Date: 21 October 2026 | Status: Draft; commands require environment inventory

Every runbook must name owner/support hours, trigger, user impact, safe diagnostics, corrective actions, escalation, verification and audit record. No guessed resource IDs or destructive commands are approved.

| Runbook | Initial response | Recovery verification |
| --- | --- | --- |
| API/dependency outage | Check synthetic journey, service health, dependency errors and recent release | Journey succeeds; latency/error rate recovers |
| Outbox backlog | Inspect oldest age, relay health, broker authorisation/throttling; preserve records | Backlog drains without data loss |
| DLQ replay | Inspect safe metadata, fix cause, authorise bounded replay preserving event ID | No duplicate side effects; replay audited |
| Database throttling | Inspect request cost/concurrency/retry; avoid retry storm | User latency/error and capacity stabilise |
| Advice failure/quota | Inspect safe job/model metadata, quotas and validation outcome | Recoverable jobs terminal; usage reconciled |
| Photo processing | Check pending intents, content validation and worker health | Ready/rejected states consistent; orphan cleanup verified |
| Payment/Xero reconciliation | Compare authoritative provider/accounting references, deduplicate | Entitlement/accounting state consistent; no duplicate charge/entry |
| Restore | Use approved backup procedure in isolated scope, including Advisor PostgreSQL/pgvector | RPO/RTO measured; input snapshots, access/deletion/outbox/commercial replay verified |
| Credential compromise | Restrict affected identity, rotate where needed, preserve audit | Exposure closed and affected access reviewed |
| Bad release | Stop promotion; approved rollback/forward fix | App/database compatible; critical journeys pass |

Production readiness requires an exercised restore and assigned alert responders. See [observability](../architecture/observability.md), [data](../architecture/data.md), [delivery](../engineering/delivery.md).

## Accepted worker baseline — 20 October 2026

See [asynchronous-processing design](../architecture/asynchronous-processing.md). Service-owned workers use only their owner's stores; core CRUD stays synchronous with local outboxes. Advice/photo handlers are durable asynchronous workflows. One namespace routes relevant commands/events; direct telemetry is not a queued business task. Shared-plan compute requires capacity/concurrency verification.

## Shared restore boundary

ReferenceProjectsDb and Cosmos ReferenceProjects are platform-owned shared databases. Coordinate restores/capacity incidents with the platform owner and other consuming projects. Logical Aquarium schema/Tracking container ownership does not provide independent physical restores; plan reconciliation of outbox/inbox/deletions and other projects before production.

## Development alert response ownership

OBS-03/[ADR-017](../architecture/decisions/adr-017.md): human project owner is initial Development responder, best effort during normal development hours with no overnight/24-hour coverage or response SLA. Route actionable alerts to an owner-designated email address (pending). Alerts link to affected service/safe diagnostics/recovery procedure; group repeats and notify on recovery. Reassess public support/escalation before Stage 4 launch. No notification setup or delivery verification claimed.

## Development alert thresholds — accepted 21 October 2026

OBS-04: initial Development investigation triggers, applied only as workloads become operational:

| Signal | Accepted Development trigger |
| --- | --- |
| API failures | HTTP 5xx rate >5% over 10 minutes with at least 20 requests |
| Low-traffic safeguard | At least 5 HTTP 5xx responses within 10 minutes, regardless of percentage |
| Unpublished outbox | Oldest pending record >5 minutes |
| Dead-letter messages | Any increase in DLQ count |
| Waiting commands | Oldest waiting command >10 minutes |
| Worker failures | At least 3 failed processing attempts within 10 minutes, including retries |

Exclude expected validation/access denials from unexpected API failure counts. Review thresholds after observing traffic. Successful processing drives applicable recovery notifications; DLQ alerts require investigation, not automatic replay. Latency, CPU/memory and dependency throttling are initially dashboard signals; alert settings follow agreed performance targets/measured shared-plan behaviour. These triggers are not availability guarantees. Exact evaluation cadence, signal scope/aggregation, recovery windows and implementation remain pending.

See [observability](../architecture/observability.md) and [ADR-017](../architecture/decisions/adr-017.md). On DLQ increase, investigate failure reason and business state before separately authorised replay. No automatic replay is approved.
