# Service boundaries

Version: 0.7 | Date: 20 October 2026 | Status: Proposed

| Service | Responsibility | Owned persistence |
| --- | --- | --- |
| Aquarium | Users, tanks/access, definitions, entitlements, payment/accounting adapters | Azure SQL |
| Tracking | Measurements, maintenance, observations, trends and photo lifecycle | Cosmos and Blob Storage |
| Advisor | Jobs, context assembly, curated retrieval, inference, evaluation metadata | Advisor-owned PostgreSQL with pgvector: relational state and curated retrieval (accepted) |

Billing begins as an isolated Aquarium module; extraction requires an ADR. Workers belong to the service whose data they change. The generic Event Processor is removed. Each service owns a separate Async Worker Function App; Tracking photo processing is functions within Tracking's app.

## Components

- Aquarium: endpoints, access policy, tank/definition modules, entitlement/billing adapter, persistence and outbox relay.
- Tracking: endpoints, validation, write/query handlers, bounded upload endpoint, photo worker, persistence and outbox relay.
- Advisor: job API, quota reservation, context builder, retrieval/model adapters, output validator and job worker.

Dependency rule: API and Infrastructure depend on Application; Application depends on Domain. Domain has no HTTP, Azure or ORM dependency. Separate projects only where useful.

## Service collaboration

- No direct cross-service database reads or writes.
- Tracking gets access/definitions from Aquarium.
- Advisor gets authorised profile/entitlement from Aquarium and history from Tracking.
- Authenticate workloads and convey verifiable actor/tank context; client user-ID headers are not trusted.
- Authorisation fails closed if the authority is unavailable; accept the availability tradeoff explicitly.
- Later projections require freshness and revocation design.
- Tracking owns latest-reading queries; do not duplicate them in Aquarium initially.
- No distributed transaction across services. Use local transactions and recoverable workflows.

Three services are the full product target. First-release deployment of Advisor can wait until the later AI slice; do not create a nonfunctional deployed service solely to satisfy a count.

## Accepted refinements

Tracking receives photo binaries through APIM, enforces the 5,242,880-byte cap before Blob persistence and owns processing/status. The browser no longer uploads directly to Blob. Advisor uses PostgreSQL for jobs/results/quotas, request snapshots and curated reference/embedding retrieval; no separate Advisor Azure SQL database or AI Search service is planned. Aquarium retains Azure SQL. Other service-boundary proposals retain their existing approval status.

## Accepted asynchronous baseline — 20 October 2026

Core CRUD commits synchronously with a local outbox. Workers relay outboxes and perform justified deferred work; one Service Bus namespace supplies separate queues/subscriptions. Read APIs access their owned stores directly. Aquarium/Advisor never write Tracking Cosmos. Three Function Apps target the existing shared App Service Plan subject to verification; logical separation does not imply independent compute scaling. See [async architecture](asynchronous-processing.md) and [approval record](../engineering/authorised-decisions-2026-10-20.md).

## Accepted parameter ownership and ingestion validation

ADR-023 accepts Aquarium ownership of definition SQL records, revisions/rules and tank selection. Tracking calls Aquarium once per new panel with all referenced definition IDs/revisions and trusted actor/tank context; applies authoritative rules before committing the panel/outbox. Reject stale definitions; fail closed on dependency failure with preserved UI input. UI entry definitions come from Aquarium, historical readings from Tracking. Commercial module boundaries remain separately subject to their existing decision status.

## Accepted shared data hosting

Aquarium owns its Aquarium schema/tables/migrations within platform-owned ReferenceProjectsDb; runtime API/worker access is schema-scoped. Tracking owns containers/indexes/lifecycle in platform-owned Cosmos ReferenceProjects, with accepted /tankId partition and container-scoped API/worker access. Platform retains database/capacity/SKU ownership. Logical service ownership is unchanged; no shared-table cross-service access. See [ADR-024](decisions/adr-024.md).

## Accepted Development hosting

Each service API is its own containerised App Service app on the shared Linux plan alongside worker Function Apps. Own identities/configuration/deployment remain separate; compute is shared. Browser calls use APIM; necessary internal calls remain permitted only under verified source rules and workload/actor authorisation (ADR-026). Configuration/secrets follow ADR-027.

## Accepted internal structure and stack

ADR-002 accepts Domain, Application, Infrastructure and API/Functions host roles; service API/worker reuse Application/Domain code. Domain has no vendor/persistence/HTTP dependency, Application defines narrow interfaces, Infrastructure adapts clients and hosts compose. Shared technical primitives only across services; no mandated per-class interfaces/repositories.

ADR-028 accepts .NET 10/C# 14, relational EF Core 10, isolated Functions compatibility gate and direct Cosmos SDK for Tracking Infrastructure. Exact patches/providers remain to be verified. Angular 22 client SPA/strict TypeScript and Vitest are accepted frontend baseline.
