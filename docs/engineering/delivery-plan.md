# Staged delivery plan

Version: 0.3 | Date: 19 October 2026 | Status: Draft; staged delivery and first-release product direction confirmed

## Delivery approach

Deliver the application incrementally. Each stage produces reviewable deliverables and demonstrates usable behaviour with relevant failure handling. A completed engineering stage is not automatically a public release.

The first public release contains tracking, maintenance and charts. Paid AI and integrations follow. Photos and deterministic dosing remain in scope; their placement after the first release is proposed and may be resequenced independently of AI. Stage detail and exit criteria below remain proposals requiring approval; no dates or effort estimates are committed.

## Stage overview

| Stage | Deliverable | Release milestone | Dependencies |
| --- | --- | --- | --- |
| 1 | Approved foundations and development environment | Internal engineering baseline | Applicable design, platform access and budget decisions |
| 2 | Secure tank and measurement vertical slice | Internal working application | Stage 1 |
| 3 | Reliable tracking and correction history | Internal release candidate foundation | Stage 2 |
| 4 | Maintenance, observations and charts | First public release | Stage 3 and production-readiness checks |
| 5 | Evaluated contextual AI | Internal AI pilot | First-release history and approved AI design |
| 6 | Paid AI and subscription management | Subsequent public release | Stage 5 and commercial-policy/provider approval |
| 7 | Photo upload and image processing | Subsequent feature release; timing proposed | Core application and approved photo design |
| 8 | Deterministic dosing calculator | Subsequent feature release; timing proposed | Tank/measurement data and reviewed formulas/products |
| 9 | Xero accounting integration | Subsequent integration release | Commercial records and approved accounting mapping |

## Stage 1 — Foundations

### Deliverables

- Inventory shared-platform resources, ownership, permissions, regions and capacity.
- Agree applicable architecture, versions, environment topology, cost estimates/low-cost tiers and proposed recovery targets; budget remains unset.
- Establish local development dependencies, configuration/secrets handling and repeatable setup documentation.
- Establish repository checks, container build conventions, delivery controls and baseline telemetry.
- Define identity configuration, API access and per-tank authorisation contracts for the first slice.

### Exit criteria

Applicable decisions are recorded, setup/check instructions are reproducible, and authorised deployment scopes are understood. Provision only approved stage dependencies; do not provision unused Advisor/AI infrastructure for the first release.

## Stage 2 — Secure tank and measurement vertical slice

Requirements: FR-001, FR-002 and the basic FR-003 journey.

### Deliverables

- Registration/sign-in and owner-to-tank access enforcement.
- Single-owner tank creation/configuration for general freshwater/marine tracking, timezone and water-volume fields.
- Parameter definitions, explicit units and basic measurement-panel entry.
- Authorised measurement write/read through the UI, gateway and owning services.
- Input validation, clear errors and telemetry across the complete journey.

### Exit criteria

An owner can sign in, configure a tank, save a valid panel and retrieve it. Unauthenticated and cross-owner requests fail; incompatible units are rejected. End-to-end behaviour and applicable contracts are verified.

## Stage 3 — Reliable tracking and history

Requirements: complete FR-003 and FR-004; applicable messaging, compatibility and recovery NFRs.

### Deliverables

- Custom parameter definitions and lifecycle rules needed for historical readings.
- Corrections with prior revisions, actor/time/reason and optimistic concurrency.
- Idempotent submissions and reliable publication under the approved outbox/event design.
- Duplicate-safe consumers where required; backlog/DLQ diagnostics and recovery procedures.
- Bounded historical queries, pagination and measured-versus-recorded timestamp handling.

### Exit criteria

Retry and stale-edit scenarios behave correctly, corrections retain provenance, and a broker outage does not lose an accepted reading. Recovery/replay checks demonstrate no duplicate business effects. Data-access isolation remains intact.

## Stage 4 — Maintenance, observations and charts

Requirements: FR-005–008, plus first-release FR-001–004 and applicable NFRs.

### Deliverables

- Plan, reschedule, cancel and complete maintenance tasks.
- Record completed maintenance, observations, water changes, dosing history and test-method changes.
- Parameter charts with time filters, visible gaps, units and optional maintenance/change overlays.
- Dashboard with latest readings and their age, upcoming work and recent activity.
- Accessible critical journeys, operational alerts/runbooks and tested backup/restore procedures.
- Approved first-release retention/privacy controls. Resolve the proposed FR-015 export/delete scope explicitly before release.

### Exit criteria — first public release

Tracking, maintenance and charts work together against approved acceptance criteria. Owner-isolation, accessibility, representative load and recovery checks pass against agreed targets. Applicable monitoring/support, release approval and deployment controls are in place; unresolved release blockers are closed or explicitly accepted by the human owner.

Recording a historical dose here does not include calculating or recommending a dose; that is Stage 8.

## Stage 5 — Contextual AI pilot

Requirement: FR-011 in an internal or controlled pilot; public paid access waits for Stage 6.

### Deliverables

- Advisor job API, scoped context assembly and asynchronous execution/status handling.
- Reviewed/versioned knowledge corpus and pgvector retrieval in Advisor-owned PostgreSQL, plus approved Foundry inference integration. PostgreSQL also stores jobs/results/quotas; no Advisor SQL or AI Search deployment.
- Structured output, valid evidence/citations and explicit missing/stale/conflicting-data handling.
- Scrollable Advice history list; selected advice exposes immutable submitted parameter values/units/times. Photos are excluded from AI context throughout this pack.
- Prompt-injection/isolation safeguards, quota/cost controls and recoverable provider failures.
- Versioned usefulness, grounding and safety evaluations with operational telemetry.

### Exit criteria

The approved evaluation gates pass and pilot access is explicitly controlled. AI outage does not prevent tracking. Model, prompt, corpus, cost and data-handling choices are recorded. Pilot authorisation does not bypass the eventual FR-014 commercial-access requirement.

## Stage 6 — Paid AI and subscriptions

Requirements: FR-012 and FR-014, completing the public release of FR-011.

### Deliverables

- Approved free/paid feature policy, pricing, quotas and payment-provider choice.
- Checkout and subscription-management journeys within the selected provider's supported model.
- Server-side entitlements, validated/idempotent webhooks and provider reconciliation.
- Usage reservation/settlement and defined cancellation, access-change and failure behaviour.
- Billing support procedures and negative tests for premium access.

### Exit criteria

Paid access is granted only from validated server-side commercial state. Duplicate/out-of-order notifications and provider outages recover correctly. Public AI meets Stage 5 quality gates and approved commercial/support policies.

## Stage 7 — Photos and image processing

Requirement: FR-010. Can be scheduled after Stage 4 independently of Stages 5–6 once approved.

### Deliverables

- UI checks exact 5,242,880-byte file limit and provides feedback. Binary uploads through APIM to Tracking; Tracking enforces actual bytes before Blob persistence and returns 413 on excess. No browser upload SAS or second completion call.
- Private quarantine, content validation/scanning, metadata stripping and processing-status handling.
- Worker creates cropped 400 x 400 WebP thumbnails and padded 1200 x 800 WebP heroes; retain originals for future processing, with authorised viewing/maintenance association. Future gallery uses thumbnails that open heroes.
- Retry, abandoned-upload/orphan reconciliation and retention/deletion handling.
- Accepted resizing/format/dimension/original-retention rules are recorded in ADR-016. Define remaining WebP quality, crop alignment, padding colour, upscaling, source-format and decoded-pixel limits before implementation.

### Exit criteria

Implement accepted ADR-016 and resolve its remaining settings first. Ready images meet accepted dimensions and the approved remaining quality rules; rejected or unprocessed content cannot be viewed. Upload/processing failures are recoverable and cross-owner access is prevented.

Record processing decisions in FR-010, the data/dynamic-flow specifications and ADR-016 as appropriate. The owner has accepted the byte limit, crop/pad dimensions, WebP output and original retention; remaining settings are not implicitly approved.

## Stage 8 — Dosing calculator

Requirement: FR-009. Can be scheduled after Stage 4 independently of AI/photos once approved.

### Deliverables

- Reviewed product/concentration catalogue and authoritative, versioned formulas.
- Deterministic calculations using explicit volume, units, current/target readings and validated limits.
- Input validation, result explanation and calculation provenance.
- Reference-case, unit-conversion, boundary and invalid-input tests.

### Exit criteria

Domain review and deterministic tests validate the approved formulas/products and supported cases. Missing concentration or incompatible units cannot yield an invented dose. No autonomous physical dosing is introduced.

## Stage 9 — Xero accounting integration

Requirement: FR-013. Timing remains proposed; retain the requirement even if release sequencing changes.

### Deliverables

- Approved commercial-to-accounting mapping, reconciliation policy and permissions.
- Secure integration/token lifecycle and external record references.
- Retry/idempotency controls, visible sync state and operator recovery.
- Verification for duplicate records, outages, partial failure and reconciliation.

### Exit criteria

Approved records reach Xero without duplicate accounting effects, failures are recoverable, and the accounting owner accepts the mapping and reconciliation evidence. Xero failure does not interrupt core aquarium tracking.

## Gates applying to every stage

Before implementation: accepted applicable ADRs, complete slice contracts, verified runtime/tool support, scoped issues/acceptance criteria, resource permissions and applicable human approval.

Before completion: meaningful behaviour/failure verification, security and telemetry review, current documentation/traceability, recovery instructions and [Definition of Done](definition-of-done.md) evidence. Human approval is required before merge; deployment/spend needs applicable authorisation.

Track requirements, issues, tests and PRs in the [traceability register](traceability.md). Keep [product scope](../requirements/vision-and-scope.md), [functional requirements](../requirements/functional-requirements.md) and the [decision register](decision-register.md) consistent as stage decisions are approved. This plan changes delivery organisation, not the authoritative Structurizr architecture or ADR acceptance status.

## Change history

| Version | Date | Change |
| --- | --- | --- |
| 0.1 | 8 October 2026 | Initial proposed delivery sequence |
| 0.2 | 14 October 2026 | Explicit stages, deliverables, dependencies and exit criteria; preserves confirmed first-release scope and proposed later timing |
| 0.3 | 19 October 2026 | Incorporates accepted scope, cost, photo upload/processing, Advice history and PostgreSQL decisions; later-stage timing remains proposed |
