# Non-functional requirements

Version: 0.2 | Date: 19 October 2026 | Status: Draft — numeric NFR targets Proposed; explicit photo byte/dimension limits Accepted

| ID | Area | Acceptance target |
| --- | --- | --- |
| NFR-001 | Availability | 99.5% monthly for core authenticated API journeys |
| NFR-002 | Latency | p95 <=750 ms for standard reads/writes under agreed load; excludes uploads and AI execution |
| NFR-003 | Load | 50 concurrent active owners; seed 1,000 owners, five tanks each, ten readings/tank/day |
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

At this profile, readings grow by approximately 18.25 million/year. Tests must use representative documents and query shapes. Transaction latency measurement includes normal authorisation dependencies; report cold starts and degraded behaviour separately rather than hiding them.

Owner: human architect, with product/operations review. Baseline infrastructure budget remains unset. Service SLAs do not establish application availability. Recovery targets must be tested against chosen tiers and backup scope. Alerts require minimum-volume guards and operational owners.

## Accepted cost and upload constraints

Australia East is preferred, subject to actual service availability. No numeric budget is approved. Avoid unnecessary always-on resources and duplicated retrieval services; compare suitable low-cost tiers against the agreed workload/recovery requirements. User approval for spending remains required.

Photo file payload maximum is exactly 5,242,880 bytes. Request-envelope limits must distinguish multipart overhead from file size; actual bytes are enforced by Tracking. A small compressed source does not establish a safe decoded memory footprint; a separate pixel/resource limit remains TBD.
