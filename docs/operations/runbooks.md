# Operational runbook specifications

Version: 0.2 | Date: 19 October 2026 | Status: Draft; commands require environment inventory

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
