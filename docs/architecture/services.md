# Service boundaries

Version: 0.2 | Date: 19 October 2026 | Status: Proposed

| Service | Responsibility | Owned persistence |
| --- | --- | --- |
| Aquarium | Users, tanks/access, definitions, entitlements, payment/accounting adapters | Azure SQL |
| Tracking | Measurements, maintenance, observations, trends and photo lifecycle | Cosmos and Blob Storage |
| Advisor | Jobs, context assembly, curated retrieval, inference, evaluation metadata | Advisor-owned PostgreSQL with pgvector: relational state and curated retrieval (accepted) |

Billing begins as an isolated Aquarium module; extraction requires an ADR. Workers belong to the service whose data they change. Event Processor is a deployment role, not a fourth service with unrestricted database access.

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
