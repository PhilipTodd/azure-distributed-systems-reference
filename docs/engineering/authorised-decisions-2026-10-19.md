# Authorised design decisions — 19 October 2026

Version: 0.2 | Date: 19 October 2026 | Status: Draft specification; authorised decisions identified below

## Authority and scope

Approval evidence: the human owner's “Decisions” message, subsequent exact-byte/crop/pad clarification, acceptance of upload-through-Tracking enforcement, and instruction “Update the pack to include the authorised changes” in this chat on 19 October 2026.

These are accepted design decisions. They do not approve unrelated proposals, application implementation, deployment, spending, migration or merge.

| ID | Accepted decision | Primary records |
| --- | --- | --- |
| DEC-01 | Single-owner tanks | ADR-021; FR-002 |
| DEC-02 | Prefer Australia East; budget unset; choose appropriate low-cost hosting tiers | ADR-022 (partial acceptance); NFR-012 |
| DEC-03 | General aquarium tracking, including freshwater and marine | Vision; FR-002–003 |
| DEC-04 | Maximum original upload 5,242,880 bytes (5 MiB); UI feedback plus strict server enforcement through Tracking | ADR-016; FR-010; API-014 |
| DEC-05 | Worker produces WebP thumbnail 400 x 400 by cropping and hero 1200 x 800 by padding | ADR-016; FR-010 |
| DEC-06 | Retain original for future processing; gallery is future scope, thumbnail opens hero | Data; UX; ADR-016 |
| DEC-07 | Advice page has scrollable history list and selected advice exposes parameter values actually submitted with the request | FR-011; AI; UX |
| DEC-08 | Photos excluded from AI context throughout this pack | FR-011; AI |
| DEC-09 | One Advisor-owned Azure Database for PostgreSQL Flexible Server replaces proposed Advisor SQL and AI Search; relational jobs/results/quotas and reference passages/metadata/pgvector embeddings | ADR-015; data; C4 source |

## Remaining specification choices

WebP compression quality, crop alignment, padding colour, upscaling policy, accepted source formats and decoded-pixel/resource limits remain TBD. The previously proposed 25-megapixel cap is not accepted. Original retention duration and deletion/privacy policy remain to be specified; retention for reprocessing is accepted.

PostgreSQL engine/extension versions, embedding model/dimensions, index strategy, connection settings, sizing and backup policy remain TBD. Exact cloud tiers/costs are not selected and budget is not set.

## Model scope

Authoritative C4 source is [Structurizr](../architecture/structurizr/workspace.dsl). Update selected PostgreSQL and photo paths there; do not replace it with independent Mermaid C4 views. Other model discrepancies remain tracked in [C4 reconciliation](../architecture/c4.md).
