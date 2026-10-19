# Observability architecture

Version: 0.1 | Date: 8 October 2026 | Status: Proposed

Use OpenTelemetry for HTTP, persistence, messages and AI calls. Propagate trusted W3C trace context and message properties; keep event ID distinct from trace ID. Link delayed/replayed processing to original causation. Safe fields: service/environment/operation/outcome/duration/error code. Pseudonymous owner references only where justified.

Never log tokens, SAS URLs, full prompts, raw private notes or image content. Separate auditable business/security records from sampled diagnostics. Define retention, sampling and access before production.

| Signal | Proposed alert |
| --- | --- |
| API failures | >2% /15 min with minimum-volume guard |
| Oldest unpublished event | >5 min |
| DLQ | Any new message |
| Advice latency | Sustained NFR-005 breach |
| SQL/Cosmos throttling | Sustained retry or user-visible failure |
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
