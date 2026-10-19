# Functional requirements

Version: 0.2 | Date: 19 October 2026 | Status: Draft

Scope is inherited from the handover unless labelled Added proposal. Acceptance criteria and detailed phasing require approval. Every requirement is owned by the product owner; design accountability sits with the human architect.

| ID | Requirement | Acceptance baseline | Phase |
| --- | --- | --- | --- |
| FR-001 | Register/sign in | External identity maps to internal user; unauthenticated API access rejected | First release |
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
