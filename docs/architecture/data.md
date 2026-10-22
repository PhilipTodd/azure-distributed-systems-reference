# Data architecture

Version: 0.8 | Date: 21 October 2026 | Status: Draft specification; authorised decisions identified below

## Approval scope

Accepted: [DEC-04–09](../engineering/authorised-decisions-2026-10-19.md). Local transactional outboxes and store ownership are accepted on 20 October (ADR-003/007); /tankId partitioning and shared schema/container placement are now accepted in ADR-005/024; index/settings details and other unchanged proposals still need approval.

## Aquarium — Azure SQL

Users, Tanks, TankAccess, ParameterDefinitions, ParameterDefinitionRevisions, Entitlements, BillingEvents, AccountingSync, Outbox and Inbox. Single-owner tanks are accepted. Aquarium uses the Aquarium schema within platform-owned ReferenceProjectsDb; tables, Outbox/Inbox, migrations and EF migration history stay schema-scoped. No separate Aquarium SQL database is created. Runtime access is limited to this schema; deployment/migration permissions are separately delegated.

## Advisor — PostgreSQL with pgvector

Accepted: one Advisor-owned PostgreSQL database with pgvector on platform-owned Flexible Server hosting replaces proposed Advisor SQL plus Azure AI Search (ADR-024 ownership refinement). Relational tables include AdviceJobs, AdviceResults, AdviceInputSnapshots, QuotaReservations, Outbox and Inbox. Knowledge tables include ReferenceSources, ReferencePassages and Embeddings with source/version/approval metadata.

Use pgvector for embedding similarity retrieval with metadata filters. No other service directly writes Advisor data. Exact types, embedding dimensions/model, vector index, migrations, connection pooling and sizing require detailed design/testing. EF Core 10 relational baseline is accepted; select/pin a compatible PostgreSQL provider before implementation; do not assume SQL Server migrations are portable.

AdviceInputSnapshots preserve actual submitted parameter values, units, qualifiers, measured times and source revisions. Historical advice must not re-query current readings as a substitute for original inputs. Snapshots follow the eventual privacy/deletion/retention policy. Curated knowledge stays separate from private tank history; no photos or image embeddings are supplied as AI context.

Use a local PostgreSQL transaction for job/quota/outbox work where designed. Do not imply exactly-once model calls.

## Tracking — Cosmos

Accepted /tankId partition with generated globally unique IDs in Tracking-owned containers within platform-owned ReferenceProjects database. Partition key is not authorisation. Typed records include panels/revisions, tasks/events, observations/dosing, photo metadata, idempotency, inbox and immutable outbox.

Index type/effective time/parameter/task state as needed, excluding unqueried text. Validate growth/hotspots/cost and capacity headroom before production; acceptance does not imply tests passed. State/outbox must share a container and logical partition for a transactional batch. Relay may duplicate; consumers deduplicate and use entity revisions. Never expire unpublished events.

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

## Accepted write/worker ownership — 20 October 2026

Tank, measurement, maintenance and observation CRUD commits synchronously to its owner's store, atomically with local outbox. Workers publish outboxes; asynchronous advice/photo handlers update only their own service's job/state/history. Tracking Cosmos is Tracking History Store, not a common event sink for Aquarium or Advisor. Telemetry is separate. Optional event-derived timeline projections require a Tracking consumer and approved requirement, not cross-store writes. See [async architecture](asynchronous-processing.md).

## Accepted measurement-panel design — 20 October 2026

Aquarium SQL ParameterDefinitions is a proposed physical table name with GUID definition identity, versioned validation/units and tank associations. Tracking persists panels with shared tank/measured time and an array of definition-ID/revision/value/unit/qualifier readings. This is a logical cross-service reference, not an enforced SQL/Cosmos foreign key. Preserve scientific revisions. Optional per-reading display snapshots remain proposed.

Before a new panel transaction, Tracking batches references into one authorised Aquarium call and rejects stale/invalid definitions or unavailable validation context; no partial save/outbox. See [ADR-023](decisions/adr-023.md). Same-container/same-partition atomicity and /tankId are accepted under ADR-005; shared database/container ownership follows ADR-024.

## Accepted shared-host isolation

ReferenceProjectsDb and Cosmos ReferenceProjects are platform-owned physical databases; Parameter Pilot owns Aquarium schema and Tracking containers. Do not modify other apps' schemas/containers or shared throughput. Logical ownership does not provide independent capacity/restore. In Cosmos, state and its outbox must share a container as well as tankId; one partition key across different containers cannot form an atomic transaction. See [ADR-024](decisions/adr-024.md) and [inventory](../infrastructure/platform-inventory.md).

## Accepted persistence implementation boundary

Tracking uses Azure Cosmos DB .NET SDK in Infrastructure, not EF Core Cosmos provider (ADR-028). Domain/Application depend on narrow interfaces; API/worker share service-local use cases (ADR-002). Relational stores use EF Core 10 and compatible providers. Exact versions/query/index/recovery settings remain readiness work. No data migration or executable persistence code is introduced.

## Definition consistency — accepted 21 October 2026

MEAS-09: Aquarium validation is the definition-consistency point for a new panel. Aquarium validates submitted revisions and returns authoritative rules; Tracking applies those rules and persists exact definition IDs/revisions with the panel. A definition change after successful validation does not invalidate that accepted panel; the next new submission uses then-current definitions. Retain historical definition revisions so saved readings remain interpretable. A stale revision detected during validation returns the accepted 409 with input preservation.

No second Aquarium validation call or distributed SQL/Cosmos transaction is introduced. This consistency rule is limited to definition changes; it does not waive token validation or tank-ownership checks. Existing fail-closed dependency behaviour and same-container/partition local atomicity remain. Timing/retirement scenarios must be verified; no executable behaviour changed.
