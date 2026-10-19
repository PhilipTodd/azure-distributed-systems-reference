# Data architecture

Version: 0.2 | Date: 19 October 2026 | Status: Draft specification; authorised decisions identified below

## Approval scope

Accepted: [DEC-04–09](../engineering/authorised-decisions-2026-10-19.md). Cosmos partitioning/outbox choices and other unchanged proposals require their own approval.

## Aquarium — Azure SQL

Users, Tanks, TankAccess, ParameterDefinitions, ParameterDefinitionRevisions, Entitlements, BillingEvents, AccountingSync, Outbox and Inbox. Single-owner tanks are accepted. Aquarium retains Azure SQL.

## Advisor — PostgreSQL with pgvector

Accepted: one Advisor-owned Azure Database for PostgreSQL Flexible Server instance replaces proposed Advisor SQL plus Azure AI Search. Relational tables include AdviceJobs, AdviceResults, AdviceInputSnapshots, QuotaReservations, Outbox and Inbox. Knowledge tables include ReferenceSources, ReferencePassages and Embeddings with source/version/approval metadata.

Use pgvector for embedding similarity retrieval with metadata filters. No other service directly writes Advisor data. Exact types, embedding dimensions/model, vector index, migrations, connection pooling and sizing require detailed design/testing. Select a compatible .NET PostgreSQL/EF Core provider before implementation; do not assume SQL Server migrations are portable.

AdviceInputSnapshots preserve actual submitted parameter values, units, qualifiers, measured times and source revisions. Historical advice must not re-query current readings as a substitute for original inputs. Snapshots follow the eventual privacy/deletion/retention policy. Curated knowledge stays separate from private tank history; no photos or image embeddings are supplied as AI context.

Use a local PostgreSQL transaction for job/quota/outbox work where designed. Do not imply exactly-once model calls.

## Tracking — Cosmos

Proposed /tankId partition with generated globally unique IDs. Partition key is not authorisation. Typed records include panels/revisions, tasks/events, observations/dosing, photo metadata, idempotency, inbox and immutable outbox.

Index type/effective time/parameter/task state as needed, excluding unqueried text. Validate growth/hotspots/cost and alternatives before acceptance. State/outbox must share a container and logical partition for a transactional batch. Relay may duplicate; consumers deduplicate and use entity revisions. Never expire unpublished events.

[Microsoft Cosmos transactional outbox guidance](https://learn.microsoft.com/en-us/azure/architecture/databases/guide/transactional-out-box-cosmos) describes the same-partition write/change-feed approach.

## Photos — private Blob Storage

- Tracking receives each binary through its authorised API, with actual file bytes capped at 5,242,880.
- Recommended bounded temporary buffering validates size before any Blob write; exact implementation/storage quotas remain to be verified. Never buffer an unbounded body.
- Only a completed within-limit upload becomes a private quarantine original; validate content before Ready.
- Keep the original byte-preserving source for future processing. Restrict its access; do not expose embedded metadata in public derivatives.
- Create separate WebP thumbnail (400 x 400, crop) and hero (1200 x 800, pad) from the oriented original, not from one another.
- Derivatives strip metadata and record processing version, dimensions and Blob references. Both must be durable before Ready.
- Generated paths and idempotent processing prevent collisions/duplicate records. Reconcile storage/metadata failures and partial derivatives.
- Gallery delivery is future scope; thumbnail selection displays the hero.
- Original retention duration, source formats, decoded-pixel cap, encoding quality, padding colour, crop alignment and upscaling remain TBD. The earlier proposed 10 MB upload limit is superseded.

## Lifecycle and recovery

Approve retention by class. Retaining originals for reprocessing is accepted but does not override owner deletion/privacy requirements. Export/deletion propagates to snapshots, originals, derivatives and derived stores. Maintain deletion reconciliation after restore.

Restore exercises cover Aquarium SQL, Advisor PostgreSQL (including vector extension/index recovery and history snapshots), Cosmos, original/derivative reconciliation, outbox replay and commercial duplicate suppression. Version migrations and test forward repair; application rollback cannot undo destructive data changes.
