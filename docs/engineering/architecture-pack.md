---
title: Parameter Pilot Engineering & Architecture Pack
---

# Parameter Pilot Engineering & Architecture Pack

Version: 0.2 | Date: 19 October 2026 (Australia/Sydney) | Status: Draft for architectural review

Decision authority: human owner/architect. This pack is a design baseline, not implementation, deployment, spending or merge approval. Selected decisions are now accepted in the [19 October 2026 authorisation record](authorised-decisions-2026-10-19.md); all other recommendations retain their existing status.

## Confirmed direction

- First public release: tracking, maintenance and charts.
- Paid AI and integrations follow. Photos and deterministic dosing remain in scope; release timing is undecided.
- Accepted: single-owner tanks, general freshwater/marine aquarium tracking, Australia East preference and low-cost tier selection; budget remains unset.
- Accepted: Tracking-enforced 5,242,880-byte photo uploads, retained originals, 400 x 400 cropped WebP thumbnails and 1200 x 800 padded WebP heroes.
- Accepted: Advice history list with original submitted parameter snapshots; photos excluded from AI context.
- Accepted: Advisor-owned PostgreSQL/pgvector replaces proposed Advisor SQL and AI Search.
- Azure hosting, Angular, ASP.NET Core APIs, meaningful microservices, SQL, Cosmos history, Blob photos, Service Bus, containers, shared-platform reuse and contextual AI remain planning inputs.

## Pack contents

| Area | Documents |
| --- | --- |
| Evidence and authority | [Evidence register](evidence-register.md), [governance](governance.md) |
| Product | [Vision and scope](../requirements/vision-and-scope.md), [functional requirements](../requirements/functional-requirements.md), [stories](../requirements/stories.md), [NFRs](../requirements/non-functional-requirements.md) |
| UX and domain | [Journeys and screens](../ux/journeys-and-screens.md), [domain model](../domain/model.md) |
| Architecture | [Services](../architecture/services.md), [C4](../architecture/c4.md), [dynamic flows](../architecture/dynamic-flows.md), [data](../architecture/data.md) |
| Contracts | [API conventions](../api/conventions.md), [API catalogue](../api/catalogue.md), [OpenAPI draft](../api/tracking-openapi-draft.md), [events](../events/catalogue.md), [event schemas](../events/schemas.md) |
| AI and security | [AI architecture](../architecture/ai.md), [security](../architecture/security.md) |
| Azure and operations | [Azure topology](../infrastructure/azure-topology.md), [IaC and local topology](../infrastructure/iac-and-local.md), [observability](../architecture/observability.md), [runbooks](../operations/runbooks.md) |
| Engineering | [Standards](standards.md), [delivery](delivery.md), [agent governance](agent-governance.md), [Definition of Done](definition-of-done.md) |
| Decisions and planning | [ADR catalogue](../architecture/decisions/README.md), [decision and risk register](decision-register.md), [traceability](traceability.md), [delivery plan](delivery-plan.md) |
| Working templates | [Issue template](issue-template.md), [PR template](../../.github/pull_request_template.md) |

Root agent guidance and Copilot instruction/profile files preserve selective decision approval and the remaining Draft status. They do not grant architectural authority or implementation permission.

## How to review

1. Confirm release scope and domain assumptions.
2. Review service ownership, reliability, identity and contracts.
3. Resolve platform, cost, retention and recovery blockers.
4. Accept or revise individual ADRs and record approval evidence.
5. Complete and validate each slice's executable contracts/configuration before implementation.

## Completeness and limits

This is the Markdown design pack requested by the owner. API and event excerpts are reviewable contract drafts inside Markdown, not independently validated executable schemas. C4 source is authoritative Structurizr; c4.md now documents reconciliation and links rather than duplicate Mermaid architecture views. The DSL reflects authorised PostgreSQL/photo changes; unrelated model discrepancies remain documented. Full endpoint schemas, rendered/validated model exports, environment parameters and environment-specific agent tools remain readiness work. No application code, deployments or production checks are claimed.

## Change history

| Version | Change | Approval |
| --- | --- | --- |
| 0.1 | Initial pack; incorporates owner-selected tracking/maintenance/charts first release | Release direction confirmed in chat; architectural approval pending |
| 0.2 | 19 October 2026: records selective owner decisions, updates photo/Advisor design and canonical C4 source | Explicit owner chat approval; remaining pack Draft |
