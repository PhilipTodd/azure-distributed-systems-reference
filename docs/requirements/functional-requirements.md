# Functional requirements

Version: 0.9 | Date: 21 October 2026 | Status: Draft

Scope is inherited from the handover unless labelled Added proposal. Acceptance criteria and detailed phasing require approval. Every requirement is owned by the product owner; design accountability sits with the human architect.

| ID | Requirement | Acceptance baseline | Phase |
| --- | --- | --- | --- |
| FR-001 | Register/sign in | External ID PKCE/API token; independent APIM/API checks; Aquarium maps validated identity to internal user; unauthenticated access rejected | First release |
| FR-002 | Configure tanks | Single-owner freshwater/marine tanks; manage name/type/timezone/volume; other owners cannot access | First release |
| FR-003 | Record readings | Dated pH, ammonia, nitrite, calcium, alkalinity, magnesium, nitrate, phosphate and custom parameters | First release |
| FR-004 | Correct readings | Preserve prior revision, actor/time/reason; reject concurrent stale edit | First release, proposed detail |
| FR-005 | View trends | Tank/parameter/time filters, stable ordering and visible gaps | First release |
| FR-006 | Plan maintenance | Create, reschedule/cancel dated tasks in tank timezone | First release |
| FR-007 | Record maintenance | Historical completion optionally linked to a plan; retries do not duplicate it | First release |
| FR-008 | Capture changes | Observations, test-kit/method changes, additives, dosing and water changes have effective times | First release |
| FR-009 | Calculate doses | Approved deterministic formulas, explicit units/product concentration and input validation | Later timing TBD |
| FR-010 | Associate photos | Upload through Tracking, exact 5 MiB cap, worker-generated WebP thumbnail/hero, original retention and private viewing; details below | Later timing TBD |
| FR-011 | Contextual advice | Authorised/entitled owner receives grounded text advice; scrollable history and submitted parameter snapshot available; no photo context | Later |
| FR-012 | Payments | Authenticated provider events update commercial state idempotently | Later |
| FR-013 | Xero | Approved accounting mapping, visible sync failures and reconciliation | Later |
| FR-014 | Free/paid access | Server-enforced entitlement policy; no client-only premium gate | Later commercial release |
| FR-015 | Export/delete data | Scoped asynchronous export and auditable deletion workflow | Added proposal; phase approval required |

Dependencies: FR-003 depends on FR-002 and versioned definitions; FR-011 depends on FR-001–008, FR-014 and approved knowledge/model choices; FR-010 depends on storage/security approval; FR-009 depends on authoritative formula review; FR-013 depends on approved commercial/accounting mapping.

For each implementation issue, add exact scenarios, errors, data lifecycle and contract/test links. Do not interpret this register as implementation approval.

## Accepted FR-010 criteria — 19 October 2026

- Maximum file payload is 5,242,880 bytes, inclusive. UI rejects larger selections before upload and explains the limit.
- Tracking authenticates/authorises, enforces actual bytes read and returns 413 for excess. No browser upload SAS is issued.
- Only within-limit completed files reach private Blob quarantine. Failed/oversized transfers leave no accepted original or processing job.
- Worker validates/scans/decodes and creates a 400 x 400 cropped WebP thumbnail and 1200 x 800 padded WebP hero.
- Retain original for future reprocessing. Derivatives strip metadata; do not silently rewrite the retained source.
- Mark Ready only after both derivatives and their metadata are durable. Retry must not duplicate photo records.
- Future gallery uses thumbnails; selecting one displays the hero. Gallery delivery timing remains proposed.
- Verification includes limit-1/limit/limit+1 bytes, forged/missing Content-Length, unauthorised access, partial upload, invalid image, orientation, crop/pad dimensions and processing retry.
- Encoding quality, alignment, padding colour, upscaling, source-format and pixel-count policies remain TBD.

## Accepted FR-011 criteria — 19 October 2026

- Advice page lists prior requests/results with scroll-back pagination.
- Selecting historic advice exposes the parameter values actually submitted with that request, including units and measured times.
- Persist an immutable request-input snapshot rather than reconstructing it from current readings; corrections/deletions of source readings do not silently alter historical advice inputs. Approved privacy/deletion policy still applies.
- Photos, image binaries, image embeddings and photo access URLs are not AI context in this pack.
- Advisor relational state and curated knowledge retrieval use one Advisor-owned PostgreSQL database with pgvector.

## Accepted processing semantics — 20 October 2026

FR-002–008 use synchronous durable owner-store writes plus local outbox before saved confirmation. FR-010 processing runs inside Tracking Async Worker; FR-011 generation inside Advisor Async Worker, with 202/status APIs. Aquarium/Advisor never write Tracking history directly. No future bulk-ingestion feature is added to required scope. See [async design](../architecture/asynchronous-processing.md).

## Accepted FR-002/003 refinement — 20 October 2026

Aquarium SQL owns GUID-identified parameter definitions/revisions, input-validation rules and tank parameter selection. UI obtains these for entry. Tracking accepts a measurement-panel document with per-reading definition ID/revision/value/unit, batches all references into one direct Aquarium call, verifies tank eligibility/current definitions and applies returned rules before an atomic panel/idempotency/outbox write.

Reject stale revisions with actionable refresh feedback. If Aquarium cannot supply authorised validation context, save neither panel nor outbox; retain form input for retry. See [US-009](stories.md), [ADR-023](../architecture/decisions/adr-023.md) and [batch contract](../api/aquarium-validation-contract.md). Optional definition snapshots and /tankId partition acceptance are not implied.

## Accepted profile preference and minimum tank contract — 21 October 2026

PROFILE-01/TANK-01 refine FR-001/002: require explicit Metric/US customary/UK imperial preference at registration profile completion, enforced before tank creation/measurement entry. Accept minimum tank fields/rules in the [tank/profile contract](../api/tank-and-profile-contract.md). Optional positive operating volume uses explicit preferred litre/US-gallon/UK-gallon units; no ambiguous gallons or reinterpretation of prior values. FR-011 later includes snapshotted preference with immutable advice context, leaving historic advice unchanged after preference changes. No additional scope for photos as AI input.

## Initial parameter catalogue and selection — accepted 21 October 2026

MEAS-05: Stage 2 offers pH, ammonia, nitrite, nitrate, phosphate, calcium, magnesium and alkalinity. Owner explicitly selects tank definitions; Freshwater/Marine does not silently restrict the catalogue. At least one selection is required before recording a panel. Each panel may contain any non-empty subset of selected parameters; testing every selected parameter is not mandatory. Custom definition creation remains Stage 3. Aquarium owns versioned allowed units/input rules; distinguish invalid input from unusual readings and do not reject merely outside a recommended aquarium range. Exact units/analyte basis and executable rule settings remain separate contract work. No catalogue seed or application behaviour implemented. Authority: [ADR-023](../architecture/decisions/adr-023.md).

## Explicit measurement units and reporting basis — accepted 21 October 2026

MEAS-06: every seeded parameter definition explicitly specifies measured quantity, chemical reporting basis, allowed units, display label and validation rules (numeric format, permitted units and applicable bounds). No ambiguous generic ppm unit. Where reporting basis differs, use separate definition variants, especially for ammonia; the initial eight catalogue names are measurement families, not a restriction to exactly eight scientific definitions. Do not conflate total/free ammonia or elemental/compound reporting bases.

Preserve entered value and unit. Initially chart matching definitions/units together; defer automatic cross-basis conversions until reviewed. Scientific units remain independent of Metric/US customary/UK imperial profile preference. Exact seed variants, unit codes, numeric bounds/precision and executable schemas remain contract-readiness work; this approval does not assert those concrete scientific rules have been reviewed. No seed data, conversion engine or application code implemented.

## Measurement-panel contract — accepted 21 October 2026

MEAS-07: measurement-panel submission identifies the tank in the route and checks ownership server-side. Require one offset-bearing measuredAt for the panel; backdating allowed; reject times more than five minutes ahead of server time. readings contains 1–50 entries, no duplicate parameterDefinitionId. Each entry requires definition GUID, positive definition revision, numeric value, explicit unitCode and qualifier (exact, belowDetectionLimit, aboveDetectionLimit). For detection-limit qualifiers the numeric value is the limit, not an exact measurement. Optional panel testMethod max 200 characters and notes max 4,000 characters.

Require an idempotency key: same authorised submission retry returns the original outcome without another panel. Conflicting payload follows the existing conflict policy. Server generates panel ID, recordedAt UTC and revision. Validate the complete panel through the accepted single Aquarium batch and local rules before atomic panel/idempotency/outbox persistence in the same Cosmos container/partition. No partial save. Profile completion, selected-definition eligibility and accepted explicit-unit/basis rules still apply. Exact executable schemas/error extensions and numeric precision/seed rules remain readiness work; no code or test execution performed.
