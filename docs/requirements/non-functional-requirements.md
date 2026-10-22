# Non-functional requirements

Version: 0.4 | Date: 21 October 2026 | Status: Draft — NFR-002 latency target and explicit photo limits Accepted; other numeric targets retain recorded status

| ID | Area | Acceptance target |
| --- | --- | --- |
| NFR-001 | Availability | 99.5% monthly for core authenticated API journeys |
| NFR-002 | Latency | Accepted PERF-01: p95 <=750 ms standard reads/writes separately through APIM including normal dependencies; detailed boundary below |
| NFR-003 | Load | Previous 50-owner benchmark deferred by owner for reference-project scope; revisit on commercial viability; proportionate first-slice verification only |
| NFR-004 | Messaging | p95 publication delay <=30 seconds; alert oldest unpublished >5 minutes |
| NFR-005 | AI latency | 95% of accepted jobs terminal within 60 seconds under agreed model/load |
| NFR-006 | Recovery | Core-data RPO <=24 hours; RTO <=8 hours; restore exercise required |
| NFR-007 | Isolation | All cross-owner/tank negative tests pass |
| NFR-008 | Accessibility | Critical journeys pass approved WCAG 2.2 AA review checklist |
| NFR-009 | Privacy | No tokens, upload credentials, private notes or full prompts in normal telemetry |
| NFR-010 | Compatibility | Breaking API/events versioned with migration plan |
| NFR-011 | AI quality | All blocking safety/isolation cases pass; >=80% usefulness pass rate |
| NFR-012 | Cost | Budget unset; minimise hosting costs through appropriate tiers; estimate per-advice and environment costs and obtain approval before provisioning |
| NFR-013 | Retention | Approved schedule for history, photos, advice, audit, backups and deduplication |

The former large-load profile is not an initial acceptance gate. Use representative documents and query shapes in proportionate first-slice verification. Transaction latency measurement includes normal authorisation dependencies; report cold starts and degraded behaviour separately rather than hiding them.

Owner: human architect, with product/operations review. Baseline infrastructure budget remains unset. Service SLAs do not establish application availability. Recovery targets must be tested against chosen tiers and backup scope. Alerts require minimum-volume guards and operational owners.

## Accepted cost and upload constraints

Australia East is preferred, subject to actual service availability. No numeric budget is approved. Avoid unnecessary always-on resources and duplicated retrieval services; compare suitable low-cost tiers against the agreed workload/recovery requirements. User approval for spending remains required.

Photo file payload maximum is exactly 5,242,880 bytes. Request-envelope limits must distinguish multipart overhead from file size; actual bytes are enforced by Tracking. A small compressed source does not establish a safe decoded memory footprint; a separate pixel/resource limit remains TBD.

## Shared-plan workload verification

Accepted worker design requires load tests for simultaneous API, image and AI jobs, with bounded concurrency and measured CPU/memory/connection pressure. One namespace is logically separated by entities/permissions; shared-plan Function Apps do not have independent compute scaling. Exact thresholds/settings remain to be agreed; no high-volume capacity claim.

## Accepted standard API latency target — 21 October 2026

PERF-01/NFR-002: p95 <=750 ms for standard API reads and writes, measured separately under an explicitly agreed representative load. Measure through APIM to the API response, including normal authorisation dependencies, Aquarium panel validation calls and database commits. Browser-to-gateway network/UI rendering and interactive sign-in are outside this API boundary. Exclude binary uploads and asynchronous AI/image execution. Report cold starts and dependency failures separately; disclose counts/rates rather than silently omitting them.

This is an engineering target requiring validation, not a demonstrated capacity or production guarantee. If the low-cost shared platform misses it, review implementation/capacity/cost with the owner before changing the target or hosting. Representative load and exact test harness/window remain to agree. Other numeric NFRs retain their existing status.

[Approval](../engineering/authorised-decisions-2026-10-21.md).
