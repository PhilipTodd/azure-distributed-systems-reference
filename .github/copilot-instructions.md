# Parameter Pilot repository context

Status: Draft design guidance. The human owner approves architecture and merge. This file grants no implementation/deployment authority.

Start with [pack index](../docs/engineering/architecture-pack.md), [governance](../docs/engineering/governance.md), [standards](../docs/engineering/standards.md), [service boundaries](../docs/architecture/services.md) and applicable requirements/accepted ADRs.

First release: tracking, maintenance and charts. Paid AI/integrations follow. Planned stack: .NET 10/C# 14, Angular, Aquarium Azure SQL, Advisor PostgreSQL/pgvector, Cosmos/Blob, Service Bus, containerised App Service, SWA/APIM, Foundry, Bicep and GitHub Actions. Exact versions/configuration require approval.

No cross-service database access; scoped tank authorisation; local transactional outboxes; deterministic dosing only; curated knowledge separated from private history.

Current solution has no application project entries. Do not invent working build/test commands or claim tests passed. Establish actual entry points in the approved implementation task. Existing Azure DevOps deployments require deliberate migration before GitHub Actions becomes authoritative.

Follow root AGENTS.md and relevant path guidance. Keep changes scoped, verify proportionately and report evidence. Human review before merge.

Read [accepted decisions](../docs/engineering/authorised-decisions-2026-10-19.md). Single-owner/general tracking; Australia East preference and low-cost tiers; exact photo cap via Tracking with WebP crop/pad derivatives and retained originals; Advice history snapshots; no photo AI context. PostgreSQL replaces Advisor SQL and AI Search. Other design remains Draft. C4 source is Structurizr, not duplicate Mermaid diagrams.
