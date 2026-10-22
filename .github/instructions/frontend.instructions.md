---
applyTo: "frontend/**,src/web/**"
---

# frontend guidance

Status: Draft design guidance; implementation requires authorised scope and applicable accepted design.

Apply approved UX, strict TypeScript, accessible labelled controls and non-colour chart cues. Preserve failed input and distinguish measured/recorded times. API/requirement changes require coordination.

Read [pack](../../docs/engineering/architecture-pack.md), [standards](../../docs/engineering/standards.md) and root AGENTS.md. Verify discovery/applyTo support on the selected Copilot surface before adoption.

Accepted: Advice page scrollable history and selected item's original submitted parameters. Photo UI rejects >5,242,880 bytes with feedback; upload through Tracking and handle server 413/status. Future gallery thumbnail opens hero. Photos cannot be attached as AI context.

Accepted ADR-028: Angular 22, strict TypeScript/templates, standalone feature-oriented components, client-side SPA/no initial SSR and Vitest with Angular TestBed. Verify/pin supported compatible Node/TypeScript/Angular/testing patches, commit lockfile and use reviewed updates/no previews by default. Component/chart libraries and E2E tooling are not selected by this baseline.
