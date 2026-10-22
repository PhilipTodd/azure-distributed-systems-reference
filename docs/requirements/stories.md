# User stories and acceptance scenarios

Version: 0.3 | Date: 20 October 2026 | Status: Draft

| ID | Story | Requirement | Acceptance scenarios |
| --- | --- | --- | --- |
| US-001 | Owner records a test panel | FR-003 | Valid panel saved atomically; incompatible unit rejected; same idempotency key/payload returns original outcome; broker outage does not lose accepted reading |
| US-002 | Owner corrects a reading | FR-004 | Prior revision retained; stale ETag returns 412; attempted input remains available in UI |
| US-003 | Owner inspects a trend | FR-005, FR-008 | Filter/time order correct; gaps visible; overlays use effective time; correlation not stated as causation |
| US-004 | Owner completes maintenance | FR-006, FR-007 | Plan transitions once; historical completion linked; repeated command cannot duplicate completion |
| US-005 | Premium owner requests advice | FR-011, FR-014 | Check owner/entitlement/quota; disclose stale/missing data; recover from outage; history shows submitted snapshot after source edit; no photo context |
| US-006 | Owner attaches photo | FR-010 | Tracking rejects actual payload above 5,242,880 bytes; no browser upload SAS; unsafe/unprocessed content unavailable; WebP dimensions/crop/pad correct; original retained |
| US-007 | Owner configures tank | FR-002 | Valid timezone accepted; volume positive if supplied; another owner gets no tank disclosure |
| US-008 | Operator recovers failed work | NFR-004, NFR-006 | Diagnose with safe telemetry; replay idempotently; record actor/reason; verify recovery |

All stories require negative owner-isolation scenarios. Add issues, implementation and PR references only when they exist. Scheduling, billing and deletion stories need expansion before their slices begin.

## US-009 — Configure parameters and validate a panel

Status: Accepted story intent/interaction under ADR-023; detailed thresholds/schema remain Draft. Requirements: FR-002/003; correction semantics also relate to FR-004.

As an aquarium owner, I want to select the parameters I track and define additional parameters with explicit units, so that measurement entry suits my aquarium.

Acceptance baseline:

- Select built-in parameters or create custom definitions with name, quantity/analyte basis, allowed unit and validation rules.
- Keep definition identity stable and scientific revisions resolvable; retire definitions without losing historical readings.
- Entry UI retrieves the tank's selected definitions and revisions from Aquarium.
- Submit a panel to Tracking, not an independently trusted definition object.
- Tracking batches all definition references into one direct Aquarium validation-context call and applies trusted rules.
- Invalid panel/ownership or stale definition prevents the entire panel write; provide actionable errors and preserve UI input.
- Aquarium outage prevents new panel/outbox persistence; controlled retry can succeed after recovery.
- A valid panel persists atomically with its idempotency/outbox records; publication remains asynchronous.

Verification includes mixed-validity panels, stale/retired/unselected definitions, incompatible units, duplicate references, cross-owner requests and dependency failure. Exact rule values and error-schema mapping require contract review.
