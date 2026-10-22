---
applyTo: "src/services/**/*.cs"
---

# backend guidance

Status: Draft design guidance; implementation requires authorised scope and applicable accepted design.

Apply approved domain/service ownership, nullable C#, explicit mapping, cancellation, optimistic concurrency and reliable outbox/inbox semantics. Add meaningful behaviour/owner-isolation tests. No cross-service store access.

Read [pack](../../docs/engineering/architecture-pack.md), [standards](../../docs/engineering/standards.md) and root AGENTS.md. Verify discovery/applyTo support on the selected Copilot surface before adoption.

Accepted photo flow: Tracking enforces actual payload <=5,242,880 bytes before Blob persistence (413 on excess). Worker creates cropped 400 x 400 and padded 1200 x 800 WebP, retaining original. No browser upload SAS or browser completion endpoint. General aquarium tracking, single-owner tanks; consult accepted ADR-015/016/021.

Accepted workers: synchronous core CRUD with owner-local outbox, service-owned relay/handlers and owner API context; never write another service's store. No generic Event Processor. Photo functions are inside Tracking Async Worker.

Accepted ADR-023: measurement panels reference Aquarium GUID definitions/revisions. One direct authorised Aquarium rule/eligibility batch per new panel; Tracking applies trusted rules, rejects stale revisions and fails without panel/outbox on dependency failure. Optional per-reading display snapshot remains Proposed; /tankId is now Accepted in ADR-005.

Aquarium tables/outbox/inbox and EF migration history are scoped to Aquarium schema in shared ReferenceProjectsDb. Runtime identity is schema-scoped; migration identity separately controlled. Tracking containers reside in shared Cosmos ReferenceProjects and use accepted /tankId; state/outbox must share a container/partition.

Accepted ADR-009: validate applicable API/workload tokens independently of APIM; Aquarium owns trusted identity/internal-user/tank access decisions. Never trust email/body/header user IDs for ownership. Managed identities do not replace actor/tank authorisation; fail closed on missing/invalid required context. Do not persist bearer tokens.

Accepted ADR-002/028: .NET 10/ASP.NET Core 10/C# 14, relational EF Core 10 with verified providers, direct Cosmos SDK only inside Tracking Infrastructure. Service-local API/worker reuse of Application/Domain; no vendor dependencies in core or unnecessary per-class repository/interface rules. Functions isolated .NET 10/host/extensions support must be verified, not assumed.
