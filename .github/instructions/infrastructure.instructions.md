---
applyTo: "infra/**,docker/**,.github/workflows/**"
---

# infrastructure guidance

Status: Draft design guidance; implementation requires authorised scope and applicable accepted design.

Preserve platform/application ownership, least privilege, secret-free outputs, approved scopes and immutable artefacts. Validate/lint/preview without assuming deployment approval. Shared SKUs/exposure/spend need applicable human authorisation.

Read [pack](../../docs/engineering/architecture-pack.md), [standards](../../docs/engineering/standards.md) and root AGENTS.md. Verify discovery/applyTo support on the selected Copilot surface before adoption.

Accepted: prefer Australia East and suitable low-cost tiers; budget unset. Advisor PostgreSQL/pgvector replaces Advisor SQL/AI Search. No spending approval is implied.

Accepted starting host: three separately identified service Function Apps on existing shared-platform App Service Plan, subject to OS/SKU/runtime/Always On/capacity verification. One namespace with service queues and filtered event subscriptions. Bound workload concurrency; document shared compute limits.

Accepted ADR-024/005: reference platform-owned ReferenceProjectsDb and Cosmos ReferenceProjects as existing; app owns Aquarium schema/migrations and Tracking /tankId containers/indexes/lifecycle. Do not create replacement databases/change throughput or shared SKUs. Verify delegated deployment and scoped runtime rights.

Initial scope is Local/dev only under ADR-025. Do not provision Test/Production yet or modify/deploy azure-reference-platform without the owner's separate request. Required platform hosting is an external prerequisite. App resources reference approved existing hosting; naming prefixes/labels alone are not access boundaries.

Accepted ADR-018: GitHub Actions sole Parameter Pilot CI/CD authority. Plan verified migration/noncompeting cutover and retirement of legacy Azure DevOps pipelines. Shared ACR/scoped OIDC, human merge approval and dev-only initial target; platform pipeline remains separate. Do not claim implementation or delete/disable pipelines during docs-only tasks.

ADR-026 restrictions are conditional: verify APIM/workload address sets and necessary SCM/probe access before configuring deny-by-default. If not feasible revisit with owner; never silently open backends. Do not provision Front Door/WAF in initial dev. ADR-027 forbids plaintext secrets in source/outputs/browser configuration; detailed RBAC/refresh/rotation require separate decisions.

Accepted ADR-027/029: configuration at startup/controlled restart, no initial dynamic flags; documented operator rotation with verified overlap where supported; missing required startup config means not Ready, bounded retry and no insecure fallback. Individual developer Entra identities/scoped dev access; no copied workload credentials/shared accounts. Exact role/refresh/retry/credential settings still require verification.
