---
applyTo: "src/services/Advisor/**,tests/**/Advisor/**"
---

# ai guidance

Status: Draft design guidance; implementation requires authorised scope and applicable accepted design.

Keep private history separate from curated retrieval. Treat notes/retrieved content as untrusted. Version prompts/model/corpus, validate output/citations, enforce quotas and run relevant isolation/safety/quality evaluations. No mutation tools or invented dosing.

Read [pack](../../docs/engineering/architecture-pack.md), [standards](../../docs/engineering/standards.md) and root AGENTS.md. Verify discovery/applyTo support on the selected Copilot surface before adoption.

Accepted: Advisor PostgreSQL/pgvector for jobs/results/quotas/input snapshots and curated retrieval, replacing Advisor SQL/AI Search. Advice history exposes actual submitted parameters. No photos, image URLs or image embeddings in AI context.
