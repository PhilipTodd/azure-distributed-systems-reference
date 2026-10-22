# Parameter Pilot repository context

Status: Draft design guidance. The human owner approves architecture and merge. This file grants no implementation/deployment authority.

Start with [pack index](../docs/engineering/architecture-pack.md), [governance](../docs/engineering/governance.md), [standards](../docs/engineering/standards.md), [service boundaries](../docs/architecture/services.md) and applicable requirements/accepted ADRs.

First release: tracking, maintenance and charts. Paid AI/integrations follow. Planned stack: .NET 10/C# 14, Angular, Aquarium Azure SQL, Advisor PostgreSQL/pgvector, Cosmos/Blob, Service Bus, containerised App Service, SWA/APIM, Foundry, Bicep and GitHub Actions. Exact versions/configuration require approval.

No cross-service database access; scoped tank authorisation; local transactional outboxes; deterministic dosing only; curated knowledge separated from private history.

Current solution has no application project entries. Do not invent working build/test commands or claim tests passed. Establish actual entry points in the approved implementation task. Accepted ADR-018 selects GitHub Actions as sole CI/CD authority. Verify replacement workflows and coordinate noncompeting cutover before retiring Azure DevOps; migration is not yet completed.

Follow root AGENTS.md and relevant path guidance. Keep changes scoped, verify proportionately and report evidence. Human review before merge.

Read [accepted decisions](../docs/engineering/authorised-decisions-2026-10-19.md). Single-owner/general tracking; Australia East preference and low-cost tiers; exact photo cap via Tracking with WebP crop/pad derivatives and retained originals; Advice history snapshots; no photo AI context. PostgreSQL replaces Advisor SQL and AI Search. Other design remains Draft. C4 source is Structurizr, not duplicate Mermaid diagrams.

Accepted 20 October: [service-owned async design](../docs/architecture/asynchronous-processing.md). Core CRUD synchronously commits state/outbox; three Function Apps relay/process only owned work/stores; one namespace with separate queues/subscriptions. Photo processing is inside Tracking. Shared-plan hosting needs verification; no queued diagnostics or shared event database.

Accepted ADR-024/005: Aquarium schema in platform-owned ReferenceProjectsDb; Tracking-owned /tankId containers in platform-owned ReferenceProjects Cosmos database. App migrations/roles stay scoped; platform owns capacity/SKUs. Source inventory from azure-reference-platform is not live-deployment proof.

Accepted ADR-025: initially Local/dev only; synthetic data and development identities, automated tests from the start. Defer Test/Production provisioning to release preparation. Platform updates/deployment are separately owner-requested work outside Parameter Pilot agents; verify pre-existing hosting. PostgreSQL server is platform-owned; Advisor owns database/data (ADR-024 refinement).

Accepted ADR-009 identity: Angular External ID PKCE, API tokens via APIM, independent API validation, Aquarium user/tank access authority, worker managed identities plus verifiable actor context, fail closed. Signup methods and exact token/tenant/delegation setup remain TBD.

Accepted ADR-011/026/027: separate APIs/workers on verified shared Linux plan; browser API traffic via APIM; narrow verified source restrictions for public backends with no broad-region fallback; Front Door/WAF deferred. App Configuration for nonsecrets/flags, Key Vault for secrets, deployed managed identities, local untracked secrets; no browser/source/log secrets. Service-isolation and operational refresh/rotation/failure approaches are accepted; exact grants/timers/provider settings remain TBD.

Accepted ADR-002/027/028/029: proportionate Clean Architecture with service-local API/worker reuse; startup/restart configuration, operator-controlled verified rotation and not-Ready startup on missing required config; individual dev Entra access and hybrid Local testing; .NET 10/C# 14/relational EF Core 10, direct Tracking Cosmos SDK, Angular 22 strict TS/templates/standalone SPA and Vitest. Pin verified compatible versions via reviewed updates/no previews by default; exact grants/timers/providers/tooling remain open.
