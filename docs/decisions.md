---
layout: page
title: Architecture decisions
eyebrow: ADRs
description: Dated log of architecture decision records. Statuses and qualifications are preserved from each decision record.
permalink: /decisions/
---

## Expected shape of an ADR

Each record states the context, the decision, and the consequences in a page that a reviewer can finish in a few minutes. The log below is the index; it is not the decision itself. The ADR’s themselves reside in the docs/architecture/decisions project folder. The adr-template-minimal.md file serves as template for future ADR docs.

{% include callout.html type="info" title="Current ADR's" content="The list below indexes the current decision records, including proposed and partially accepted decisions. The list in this documentation site is static - as new ADR's are created they will be manually added here." %}

| Date | Status | Decision |
| --- | --- | --- |
| 26 October 2026 | Accepted | [ADR-001: Three service boundaries]({% link architecture/decisions/adr-001.md %}) |
| 20 October 2026 | Accepted | [ADR-002: Proportionate Clean Architecture]({% link architecture/decisions/adr-002.md %}) |
| 20 October 2026 | Accepted | [ADR-003: Service-owned stores and authorised context APIs]({% link architecture/decisions/adr-003.md %}) |
| 20 October 2026 | Partially Accepted | [ADR-004: Data-store responsibilities]({% link architecture/decisions/adr-004.md %}) |
| 20 October 2026 | Accepted | [ADR-005: Tracking Cosmos partition key]({% link architecture/decisions/adr-005.md %}) |
| 26 October 2026 | Accepted | [ADR-006: History without full event sourcing]({% link architecture/decisions/adr-006.md %}) |
| 20 October 2026 | Accepted | [ADR-007: Synchronous core writes and transactional outboxes]({% link architecture/decisions/adr-007.md %}) |
| 20 October 2026 | Accepted | [ADR-008: One Service Bus namespace and routed commands/events]({% link architecture/decisions/adr-008.md %}) |
| 21 October 2026 | Accepted | [ADR-009: Entra External ID, token validation and per-tank authorisation]({% link architecture/decisions/adr-009.md %}) |
| 8 October 2026 | Proposed | [ADR-010: Entitlement authority]({% link architecture/decisions/adr-010.md %}) |
| 20 October 2026 | Accepted | [ADR-011: Separate containerised API apps on shared Development hosting]({% link architecture/decisions/adr-011.md %}) |
| 20 October 2026 | Accepted | [ADR-012: Service-owned Function Apps on shared-plan hosting]({% link architecture/decisions/adr-012.md %}) |
| 8 October 2026 | Proposed | [ADR-013: Deterministic dosing]({% link architecture/decisions/adr-013.md %}) |
| 8 October 2026 | Proposed | [ADR-014: Foundry inference selection]({% link architecture/decisions/adr-014.md %}) |
| 20 October 2026 | Accepted | [ADR-015: Advisor PostgreSQL persistence and curated retrieval]({% link architecture/decisions/adr-015.md %}) |
| 20 October 2026 | Accepted | [ADR-016: Photo upload, limits and derivative lifecycle]({% link architecture/decisions/adr-016.md %}) |
| 21 October 2026 | Partially Accepted | [ADR-017: Observability and privacy]({% link architecture/decisions/adr-017.md %}) |
| 20 October 2026 | Accepted | [ADR-018: GitHub Actions as sole Parameter Pilot CI/CD authority]({% link architecture/decisions/adr-018.md %}) |
| 8 October 2026 | Proposed | [ADR-019: Payment provider]({% link architecture/decisions/adr-019.md %}) |
| 8 October 2026 | Proposed | [ADR-020: Xero release placement]({% link architecture/decisions/adr-020.md %}) |
| 19 October 2026 | Accepted | [ADR-021: Single-owner tanks]({% link architecture/decisions/adr-021.md %}) |
| 20 October 2026 | Partially Accepted | [ADR-022: Environments, cost and recovery]({% link architecture/decisions/adr-022.md %}) |
| 21 October 2026 | Accepted | [ADR-023: Aquarium parameter definitions and validated Tracking measurement panels]({% link architecture/decisions/adr-023.md %}) |
| 20 October 2026 | Accepted | [ADR-024: Shared platform ownership, Aquarium schema and Tracking containers]({% link architecture/decisions/adr-024.md %}) |
| 20 October 2026 | Accepted | [ADR-025: Local and Development initially; release environments deferred]({% link architecture/decisions/adr-025.md %}) |
| 20 October 2026 | Accepted approach; addressing feasibility unverified | [ADR-026: Development API ingress through APIM with restricted public backends]({% link architecture/decisions/adr-026.md %}) |
| 20 October 2026 | Accepted arrangement, isolation and operational policies; exact implementation settings pending | [ADR-027: Configuration, secrets and managed-identity access]({% link architecture/decisions/adr-027.md %}) |
| 20 October 2026 | Accepted baseline; exact versions/compatibility verification pending | [ADR-028: Backend, Tracking persistence and frontend technology baseline]({% link architecture/decisions/adr-028.md %}) |
| 21 October 2026 | Accepted approach; concrete tools/access pending | [ADR-029: Hybrid Local dependencies and individual developer identity]({% link architecture/decisions/adr-029.md %}) |
| 20 October 2026 | Accepted approach; setup/verification pending | [ADR-030: Automated testing and browser verification]({% link architecture/decisions/adr-030.md %}) |
