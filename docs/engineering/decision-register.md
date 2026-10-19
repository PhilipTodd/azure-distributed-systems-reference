# Decision and risk register

Version: 0.2 | Date: 19 October 2026 | Status: Draft

| Priority | Topic | Position/status | Owner / gate |
| --- | --- | --- | --- |
| High | First release | Tracking, maintenance and charts confirmed | Product owner; recorded chat direction |
| High | Aquarium scope | Accepted: general freshwater/marine tracking | Owner; DEC-03 |
| High | Tank sharing | Accepted: single-owner tanks | Architect; before access contract |
| High | Region | Accepted: Australia East preference; verify support | Platform owner; verify availability |
| High | Budget | Unset; accepted low-cost tier selection direction | Owner; before provisioning |
| High | Free/paid policy | Free tracking/paid AI; pricing/limits TBD | Product owner; before commercial release |
| High | Platform inventory | Actual resources/permissions unknown | Platform owner; before IaC approval |
| High | Units/dosing | Reviewed catalogue/formulas required | Domain reviewer; before calculator |
| High | Dependency failure | Authorisation fails closed, proposed | Architect; availability tradeoff |
| High | Recovery | NFR-006 target proposed; tier feasibility unverified | Operations; before production |
| High | AI | Model/region/cost/corpus/data handling TBD | AI owner; before AI approval |
| Medium | Payment | Stripe candidate, not selected | Product owner |
| Medium | Xero | Scope retained; later timing proposed | Product/accounting owner |
| Medium | CI authority | GitHub Actions intended; Azure DevOps observed | Engineering owner; migration |
| Medium | Agent surface | Target IDE/cloud configuration TBD | Engineering owner; before activation |
| Medium | Retention/privacy | Policy TBD | Owner; before real user data |
| Medium | Cosmos growth | Partition load/cost test needed | Data owner; before acceptance |
| Medium | Versions/licensing | Pin compatible approved dependencies | Engineering owner |
| Medium | AI drift | Versioned evaluations/rollback proposed | AI owner |

Roles are accountability placeholders, not appointed people. Accepted decisions require named approver/date/evidence. Only explicitly recorded decisions are accepted; other architectural approval remains pending.

## Accepted changes — 19 October 2026

[Approval record](authorised-decisions-2026-10-19.md) is the evidence for DEC-01–09. ADR-015/016/021 Accepted; ADR-004/022 Partially Accepted.

Photo route: API through Tracking, exact 5,242,880-byte cap; worker WebP crop/pad; retain original. Advice: history list/input snapshots; exclude photos. PostgreSQL consolidates Advisor persistence/retrieval. Remaining photo encoding/alignment/padding/upscaling limits and PostgreSQL sizing/index settings stay TBD.
