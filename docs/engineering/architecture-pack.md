---
title: Parameter Pilot Engineering & Architecture Pack
---

# Parameter Pilot Engineering & Architecture Pack

Version: 0.14 | Date: 21 October 2026 | Status: Draft for architectural review

Decision authority: human owner/architect. This pack is a design baseline, not implementation, deployment, spending or merge approval. Selected decisions are now accepted in the [19 October 2026 authorisation record](authorised-decisions-2026-10-19.md); all other recommendations retain their existing status.

## Confirmed direction

- First public release: tracking, maintenance and charts.
- Paid AI and integrations follow. Photos and deterministic dosing remain in scope; release timing is undecided.
- Accepted: single-owner tanks, general freshwater/marine aquarium tracking, Australia East preference and low-cost tier selection; budget remains unset.
- Accepted: Tracking-enforced 5,242,880-byte photo uploads, retained originals, 400 x 400 cropped WebP thumbnails and 1200 x 800 padded WebP heroes.
- Accepted: Advice history list with original submitted parameter snapshots; photos excluded from AI context.
- Accepted: Advisor-owned PostgreSQL/pgvector replaces proposed Advisor SQL and AI Search.
- Accepted 20 October: three service-owned Async Worker Function Apps; core writes stay synchronous with local outboxes; one Service Bus namespace with separate queues/subscriptions; owner-only stores and direct telemetry. Shared-plan hosting requires verification.
- Azure hosting, Angular, ASP.NET Core APIs, meaningful microservices, SQL, Cosmos history, Blob photos, Service Bus, containers, shared-platform reuse and contextual AI remain planning inputs.

30 October ownership refinement: accepted [ADR-031](../architecture/decisions/adr-031.md) places PP-exclusive App Configuration stores/Key Vaults in PP infrastructure, with deployment deferred to PP Bicep changes. Genuinely shared resources remain platform-owned. [Scoped access](../infrastructure/scoped-access-readiness.md) is the next preparation item; a dedicated platform SQL administrator group is selected, with no grants applied.

## Pack contents

| Area | Documents |
| --- | --- |
| Evidence and authority | [Evidence register](evidence-register.md), [governance](governance.md) |
| Product | [Vision and scope](../requirements/vision-and-scope.md), [functional requirements](../requirements/functional-requirements.md), [stories](../requirements/stories.md), [NFRs](../requirements/non-functional-requirements.md) |
| UX and domain | [Journeys and screens](../ux/journeys-and-screens.md), [domain model](../domain/model.md) |
| Architecture | [Services](../architecture/services.md), [C4](../architecture/c4.md), [dynamic flows](../architecture/dynamic-flows.md), [data](../architecture/data.md), [async workers](../architecture/asynchronous-processing.md) |
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

This is the Markdown design pack requested by the owner. API and event excerpts are reviewable contract drafts inside Markdown, not independently validated executable schemas. C4 source is authoritative Structurizr; c4.md now documents reconciliation and links rather than duplicate Mermaid architecture views. The DSL reflects authorised PostgreSQL/photo/worker changes; unrelated model discrepancies remain documented. Full endpoint schemas, rendered/validated model exports, environment parameters and environment-specific agent tools remain readiness work. No application code, deployments or production checks are claimed.

## Change history

| Version | Change | Approval |
| --- | --- | --- |
| 0.1 | Initial pack; incorporates owner-selected tracking/maintenance/charts first release | Release direction confirmed in chat; architectural approval pending |
| 0.2 | 19 October 2026: records selective owner decisions, updates photo/Advisor design and canonical C4 source | Explicit owner chat approval; remaining pack Draft |

## Worker approval record

See [20 October decisions](authorised-decisions-2026-10-20.md) and [async design](../architecture/asynchronous-processing.md). Stage 1 must verify shared-plan compatibility and ownership before deployment; later-stage workloads are not provisioned merely for demonstration. Other architecture/implementation remains subject to its existing approval gates.

## Measurement-panel approval

Accepted MEAS-01–04: Aquarium owns versioned parameter definitions and tank selections; Tracking validates an entire panel through one batched Aquarium call before local commit. Stale definitions and Aquarium unavailability cause no panel/outbox save; preserve UI input for refresh/retry. [ADR-023](../architecture/decisions/adr-023.md), [batch contract](../api/aquarium-validation-contract.md), [story US-009](../requirements/stories.md). Definition snapshots remain proposed. /tankId and shared Aquarium-schema/Tracking-container placement are accepted in ADR-005/024.

## Shared-platform placement approval

Accepted DATA-01–04: platform owns shared capacities/databases; Aquarium owns schema/tables/migrations in ReferenceProjectsDb; Tracking owns containers/indexes/lifecycle in ReferenceProjects; /tankId accepted. See [ADR-024](../architecture/decisions/adr-024.md), [ADR-005](../architecture/decisions/adr-005.md) and [repository inventory](../infrastructure/platform-inventory.md). Platform source inspected read-only; live deployed state/permissions remain unverified.

## Initial environments and platform prerequisite

Accepted [ADR-025](../architecture/decisions/adr-025.md): Local and Development initially; Test/Production provisioning deferred until release preparation. See [environment specification](../development/environments.md). Shared platform additions/deployment are separately owner-requested prerequisite work outside Parameter Pilot's agentic process. ADR-024 extends shared hosting to APIM/ACR/Key Vault/App Configuration/Blob/PostgreSQL; Advisor owns a database on the platform server, not the server itself. No resources were provisioned.

## Accepted CI/CD authority

[ADR-018](../architecture/decisions/adr-018.md) accepts GitHub Actions as sole Parameter Pilot CI/CD authority and migration/retirement of Azure DevOps after verified cutover. [Delivery design](delivery.md) records required PR checks, shared ACR/scoped OIDC, dev-only initial deployment and human merge approval. Platform pipelines remain external; implementation/retirement evidence is pending.

## Accepted identity approach

[ADR-009](../architecture/decisions/adr-009.md) accepts External ID PKCE, API tokens through APIM, independent API validation, Aquarium internal-user/tank access authority, managed-identity worker calls with trusted actor context and fail-closed behaviour. Initial local email-passcode registration and deferred social sign-on are subsequently accepted; exact configuration/session/MFA/delegation remains unresolved. See [security](../architecture/security.md).

## Accepted Development hosting/access/configuration

Accepted [ADR-011](../architecture/decisions/adr-011.md), [ADR-026](../architecture/decisions/adr-026.md) and [ADR-027](../architecture/decisions/adr-027.md): separate shared-plan APIs/workers, APIM browser entry, conditional restricted public backends, deferred Front Door/WAF and managed-identity App Configuration/Key Vault access. See [dev ingress](../infrastructure/development-api-access.md) and [configuration](../infrastructure/configuration-and-secrets.md). Exact addressing/capacity/grants and refresh/rotation implementation settings remain open; operational policies are accepted in ADR-027.

## Accepted operational and technology baseline

[ADR-002](../architecture/decisions/adr-002.md) accepts Clean Architecture; [ADR-027](../architecture/decisions/adr-027.md) now includes startup/restart configuration, rotation and failure handling; [ADR-028](../architecture/decisions/adr-028.md) accepts .NET 10/C# 14/EF Core 10, direct Cosmos SDK and Angular 22/strict TypeScript/Vitest; [ADR-029](../architecture/decisions/adr-029.md) accepts individual developer identities/hybrid dependencies.

Specifications: [technology baseline](technology-baseline.md), [Local development](../development/local-development.md), [configuration policies](../infrastructure/configuration-and-secrets.md). Exact patch/provider/tool/role settings remain unverified; no implementation performed.

## Accepted testing strategy

[ADR-030](../architecture/decisions/adr-030.md) accepts risk-based automated verification, applicable passing PR gates, xUnit and Playwright Test/TypeScript alongside Vitest/TestBed. See [testing strategy](testing-strategy.md) and the [Stage 1 readiness guide](stage-1-readiness.md#current-completion-path). No test or CI setup is claimed.

## Customer sign-in approval — 21 October 2026

[ID-06–08](authorised-decisions-2026-10-21.md) refine [ADR-009](../architecture/decisions/adr-009.md): dedicated External ID customer tenancy/local email-passcode flow, deferred social/federated sign-on, strict token/stable-identity isolation and visible account switching. Same-email Microsoft/customer coexistence is a required verification case. Exact setup/session/MFA/delegation remains pending.

## Accepted readiness preparation — READY-01

The owner accepted preparing a concrete Stage 2 readiness specification covering compatible versions, executable contracts, scientific seed proposals, configuration/Local instructions and platform evidence. [Approval](authorised-decisions-2026-10-21.md); [current Stage 1 completion path](stage-1-readiness.md#current-completion-path). No further high-level Q&A is presently required before this preparation. Scientific seed content/final baseline still require review; compatibility conflicts must be raised. This records the approach, not a completed specification, implementation or platform authorisation.
