# Observability architecture

Version: 0.7 | Date: 21 October 2026 | Status: Accepted Local/dev baseline and initial triggers; remaining settings pending

Use OpenTelemetry for HTTP, persistence, messages and AI calls. Propagate trusted W3C trace context and message properties; keep event ID distinct from trace ID. Link delayed/replayed processing to original causation. Safe fields: service/environment/operation/outcome/duration/error code. Pseudonymous owner references only where justified.

Never log tokens, SAS URLs, full prompts, raw private notes or image content. Separate auditable business/security records from sampled diagnostics. Define retention, sampling and access before production.

| Signal | Current position |
| --- | --- |
| API failures | Accepted OBS-04 thresholds below |
| Oldest unpublished event | Accepted >5 min; OBS-04 |
| DLQ | Accepted any increase; OBS-04 |
| Advice latency | Proposed later-stage alert: sustained NFR-005 breach |
| SQL/Cosmos/PostgreSQL throttling | Dashboard initially; alert threshold pending |
| Billing/accounting | Failed or stale reconciliation |
| Photos | Repeated failure or stale pending processing |
| Cost | Approved daily/monthly thresholds |

AI telemetry includes safe model/prompt/corpus version, token/cost counts, latency, validation failures and outcome; no full private context by default.

Illustrative workspace-based Application Insights query; validate actual schema:

```kusto
AppRequests
| where TimeGenerated > ago(1h)
| summarize Requests = count(), Failed = countif(Success == false),
    P95Ms = percentile(DurationMs, 95)
  by AppRoleName, bin(TimeGenerated, 5m)
| extend FailureRate = todouble(Failed) / Requests
```

SLOs measure complete user journeys, not isolated service promises. Alert routing, support hours and responder remain TBD. See [runbooks](../operations/runbooks.md).

## Accepted worker telemetry — 20 October 2026

All three APIs and Async Workers emit OpenTelemetry directly. Propagate trace context in Service Bus properties and preserve causation through retry/replay; do not use a business queue solely for tracing. Monitor each entity's age/backlog/DLQ, outbox age, worker failures/concurrency and shared-plan CPU/memory/connections against API latency. Routing/threshold/retention details remain proposed. Observability remains excluded from the Container diagram for readability.

## Accepted Local/Development baseline

OBS-01/[ADR-017](decisions/adr-017.md): APIs/workers use OpenTelemetry, with Development export to shared Application Insights/Log Analytics. Correlate HTTP, outbox and broker processing; structured service/operation/outcome/duration/safe-error fields. Monitor API latency/failures, dependencies, outbox age, queue backlog/DLQ and worker failures. Local console diagnostics by default, Azure export only explicitly configured. Exclude tokens, credentials, private notes, image content and full request/response bodies. Business/security audit records are separate from sampled diagnostic telemetry. Retention/sampling/alerts/responders remain separate decisions; no actual instrumentation or deployment is claimed. Diagram exclusions remain unchanged.

## Accepted Development diagnostic policy

OBS-02/[ADR-017](decisions/adr-017.md): target 30 days for diagnostic retention, subject to supported table settings/shared-platform approval. 100% distributed traces initially at low Development traffic; Information-and-above application logs, suppress routine health-check noise without hiding failures. Debug/Trace is temporary investigation-only and then disabled. Review volume/sampling before substantial load tests; coordinate source sampling across services if volume grows. Business/security audit retention remains separate. Verify effective table retention, SDK/exporter controls and costs; no shared settings changed.

## Accepted Development response ownership

OBS-03/[ADR-017](decisions/adr-017.md): project owner handles actionable Development alerts through an owner-designated email address, still to select/configure. Best-effort response during normal development hours; no overnight/24-hour coverage or response SLA. Include affected service and links to safe diagnostics/runbooks; group repeats and notify on recovery. Reassess support/escalation before Stage 4 public launch. Thresholds/configuration remain pending. No emails sent or alert resources configured.

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

Authority: [ADR-017](decisions/adr-017.md). These accepted Development triggers supersede earlier proposed generic API/DLQ/outbox wording. Later AI/photo/commercial alerts remain proposals.

## Accepted API latency measurement

PERF-01/[NFR-002](../requirements/non-functional-requirements.md): p95 <=750 ms standard API reads and writes, measured separately through APIM including normal authorisation/Aquarium validation/database commits under agreed representative load. Exclude interactive sign-in, uploads and async AI/image execution; separately report cold starts/dependency failures with counts. This is not a latency alert threshold or demonstrated capacity. Load profile/harness and latency alert settings remain pending.
