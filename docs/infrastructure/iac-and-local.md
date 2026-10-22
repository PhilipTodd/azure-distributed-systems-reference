# IaC and local topology

Version: 0.8 | Date: 21 October 2026 | Status: Proposed

## Bicep module plan

`web`, `api-hosting`, `identities`, `sql`, `cosmos-entities`, `messaging-entities`, `storage`, `configuration`, `observability`, `ai-integration`, `gateway`.

Subscription scope creates approved resource groups. Application modules operate at resource-group scopes. Shared-service changes are separate from application deployment. Environment files hold nonsecret parameters; Key Vault/identity handles credentials. Outputs never expose secrets or connection strings.

Existing Bicep establishes only resource group and Static Web App. Add approved modules incrementally with build/lint, parameter validation, exposure review and what-if. Do not claim module names above already exist.

## Local proposal

| Component | Endpoint/approach |
| --- | --- |
| Angular | 4200 |
| Aquarium API | 5101 |
| Tracking API | 5102 |
| Advisor API, later | 5103 |
| SQL development instance | 1433 |
| Azurite | Default emulator ports |
| OpenTelemetry collector | Configured OTLP endpoint |
| Cosmos/messaging | Compatible emulator where verified; otherwise isolated cloud dev resources |
| Identity/AI | Controlled development resources; deterministic test doubles |

Compose should use a named app network, persistent development volumes, health checks and nonproduction credentials outside source. Verify platform compatibility and feature coverage. Test cloud integration differences. Local ports are not public production endpoints. No runnable Compose definition is supplied by this Markdown pack.

## Accepted dependency changes — 19 October 2026

Reference separately provisioned platform PostgreSQL hosting and manage only approved Advisor database/data assets (with local PostgreSQL/pgvector when Stage 5 is developed); remove planned Advisor Azure SQL/AI Search modules. Keep Aquarium SQL. Proposed local PostgreSQL port is 5432, subject to local conflicts. Engine/extension image/provider versions need verification.

API/gateway hosting must permit bounded photo multipart overhead while Tracking enforces the exact 5,242,880-byte file limit. No browser upload SAS configuration. Image workers retain originals and write WebP derivatives. Choose low-cost suitable tiers, prefer Australia East and provision later-stage resources only when authorised.

## Accepted workers and messaging — 20 October 2026

Plan modules for three separately identified Function Apps referencing the existing platform App Service Plan, one existing Service Bus namespace and application-owned command queues/topics/filtered subscriptions. Do not deploy the generic Event Processor or standalone Photo Worker. Enable Always On where supported/required and verify hosting compatibility/capacity first. Use independent managed identities/entity permissions; do not output secrets or grant cross-store writes.

Local development runs service-owned Functions hosts and outbox functions, with deterministic tests for relay, retry, filtering and idempotency. Emulator feature coverage must be verified; use isolated cloud integration tests as required. Do not provision unused Advisor/photo compute before their stages.

## Accepted shared database resource scopes

Reference platform SQL server/ReferenceProjectsDb and Cosmos account/ReferenceProjects as existing; do not create replacement databases or change throughput. Application schema migrations create Aquarium tables/outbox/inbox and schema-scoped EF migration history. Runtime SQL access remains within Aquarium; separate narrowly scoped migration principal.

Application Cosmos modules manage approved Tracking containers/indexes with /tankId inside existing ReferenceProjects; co-locate each state/outbox transaction in the same container/partition. Data-plane access is container-scoped for Tracking API/worker. Shared-capacity changes and unapproved broader roles are platform-owner work. See [inventory](platform-inventory.md), accepted ADR-005/024.

## Initial environment and provisioning boundary

Local/dev only under accepted ADR-025. No Test/Production provisioning now; keep automated test execution active. Reference required pre-existing platform hosting instead of introducing app modules that create shared APIM/ACR/vault/config-store/storage-account/PostgreSQL-server resources. Owner will request platform changes/deployment separately. Application modules manage approved child resources/content only; concrete child APIs/permissions remain detailed readiness work. See [environments](../development/environments.md).

## Accepted Development implementation boundaries

ADR-011/026: app modules target separate API apps on existing shared Linux plan and configure narrow verified ingress restrictions only after addressing/management-access checks. Do not provision Front Door/WAF initially. ADR-027: references to platform App Configuration/Key Vault and managed identities; no embedded secret values, local secret material or browser secrets. Exact access assignments, retry/timeout and provider-specific rotation settings remain TBD; startup/restart refresh and operator-controlled rotation approach are now accepted in ADR-027. Platform resources remain separately owner-managed.

## Accepted Local and stack decisions

Use ADR-029 hybrid dependencies and individual developer Entra identities/scoped dev access. Determine emulator/cloud parity and concrete tools/versions before setup. ADR-028 stack is .NET 10/C# 14/relational EF Core 10, direct Cosmos SDK, isolated Functions compatibility gate, Angular 22/strict TypeScript/Vitest; do not assume installed versions or host support. Local secrets untracked; deployed credentials never copied locally.

## Minimum Stage 2 Local setup — accepted 21 October 2026

DEV-03: minimum Stage 2 Local setup runs Angular UI and Aquarium/Tracking APIs directly through development tooling. Docker Compose starts SQL Server Developer and Cosmos DB NoSQL emulator containers; use a small repeatable synthetic seed set. Actual Development External ID supports customer authentication/OBO. Select/pin supported compatible container/tool versions after verification; no preview assumption or floating latest pin. Local certificate and secrets follow ID-15/ADR-027.

Emulator/container results are not proof of Azure parity. Verify required operation support, including same-container/partition transactions, and real Development identity/permissions/cloud behaviour. If a required operation is unsupported locally, use the approved Development dependency for that check rather than building an inaccurate substitute. No unapproved resource creation/spend implied.

Advisor/PostgreSQL/photo dependencies wait for their stages. Add Service Bus and workers when the authorised implementation slice requires them; preserve core synchronous transaction/outbox design and do not fabricate broker-delivery evidence. Docker Compose manages dependencies, not a requirement to containerise local UI/APIs. No Compose file, dependencies, seeds, projects or resources created in this documentation update.
