---
applyTo: "src/services/**/*.cs"
---

# backend guidance

Status: Draft design guidance; implementation requires authorised scope and applicable accepted design.

Apply approved domain/service ownership, nullable C#, explicit mapping, cancellation, optimistic concurrency and reliable outbox/inbox semantics. Add meaningful behaviour/owner-isolation tests. No cross-service store access.

Read [pack](../../docs/engineering/architecture-pack.md), [standards](../../docs/engineering/standards.md) and root AGENTS.md. Verify discovery/applyTo support on the selected Copilot surface before adoption.

Accepted photo flow: Tracking enforces actual payload <=5,242,880 bytes before Blob persistence (413 on excess). Worker creates cropped 400 x 400 and padded 1200 x 800 WebP, retaining original. No browser upload SAS or browser completion endpoint. General aquarium tracking, single-owner tanks; consult accepted ADR-015/016/021.
