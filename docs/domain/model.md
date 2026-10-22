# Domain model and invariants

Version: 0.9 | Date: 21 October 2026 | Status: Draft

Aquarium is the service name; Tank is the aggregate representing an aquarium installation. They are synonyms for first-release product terminology, not two nested aggregates.

| Aggregate/record | Owner | Invariant |
| --- | --- | --- |
| Tank | Aquarium | Single owner (accepted); freshwater/marine scope; positive volume when supplied |
| ParameterDefinition / Revision | Aquarium | Stable identity; explicit quantity/units; immutable scientific revision |
| MeasurementPanel / Revision | Tracking | One tank; measured time; validated readings; correction provenance |
| PlannedMaintenanceTask | Tracking | Explicit planned/completed/cancelled transitions |
| MaintenanceEvent | Tracking | Historical event separate from plan |
| Observation / DosingRecord | Tracking | Records what happened, not implied advice |
| Photo | Tracking | One tank and authorised association; explicit lifecycle |
| AdviceRequest / Result | Advisor | Requester/tank scope and source provenance |
| SubscriptionEntitlement | Aquarium | Validated commercial state plus approved policy |
| AccountingSyncRecord | Aquarium | External reference, sync/reconciliation state |

Livestock/equipment remain optional profile extensions.

## Measurements and units

Reading fields: definition ID/revision, numeric value, unit code, qualifier, measured timestamp, server-recorded timestamp, optional test method/notes, revision and correction actor/reason.

Qualifiers: exact, below detection limit, above detection limit. A detection limit is not an exact zero. Preserve entered values/units. Canonical conversion is permitted only through reviewed dimensionally valid conversions.

| Parameter | Unit policy |
| --- | --- |
| pH | Dimensionless logarithmic quantity |
| Alkalinity | dKH and approved equivalent alkalinity units |
| Calcium/magnesium | Explicit concentration unit |
| Ammonia/nitrite/nitrate/phosphate | Explicit analyte basis and concentration unit |
| Custom | Declared quantity, allowed units and validation policy |

Compound concentration and concentration expressed as an element are not interchangeable without a reviewed conversion. Separate invalid input from unusual but plausible values; the latter should normally save with a warning.

## Time and lifecycle

- Accept offset-bearing measured times; store UTC and preserve meaningful entry context.
- Tank timezone governs date-only plans and presentation.
- Backdating is allowed; future tolerance is five minutes ahead of server time under MEAS-07.
- Retired definitions disallow new use but retain history.
- Display-name edits do not change historical scientific meaning.
- Optimistic concurrency protects correction and task transitions.
- User deletion hides records and initiates approved cleanup; retention policy remains TBD.
- Use current records plus explicit revision/audit history, not full event sourcing.

## Dosing

Version reviewed formulas and product concentrations with authoritative sources. Record volume, current/target values, units, product/formula versions, calculated quantity and validated limits.

General dimensional relationship: dose = required amount of active substance / active concentration. Product chemistry, concentration basis and safe limits must be supplied and reviewed before any runnable formula is accepted. No universal safe dose is established here.

AI may explain a validated result; it cannot invent concentrations, bypass limits or operate physical equipment.

## Accepted photo and advice semantics

A Photo has a retained original and two WebP derivatives: thumbnail 400 x 400 cropped; hero 1200 x 800 padded. State distinguishes Uploading, Uploaded, Processing, Ready, Rejected and Failed; detailed transition/concurrency contract remains draft. Photo metadata records original size and derivative dimensions/version. Originals remain private for reprocessing.

AdviceRequest includes the actual submitted parameter snapshot (IDs/revisions, values/qualifiers, units and measured times). Historic viewing reads that snapshot, not today's measurements. Photos are never included in AI context in this pack. Advice is a request/result history, not an implicit conversational thread.

## Accepted parameter-definition and panel contract — 20 October 2026

[ADR-023](../architecture/decisions/adr-023.md): Aquarium SQL owns definitions/revisions and tank selection. A GUID parameterDefinitionId identifies a definition row, not a table or SQL foreign key enforced by Cosmos. Definitions carry name, built-in/custom designation, quantity/analyte basis, units/reviewed conversions, input rules and active/retired state; scientific revisions preserve historical meaning.

Tracking stores one panel for readings measured together, with a shared tankId/measuredAt, server recordedAt and revision. Each reading has definition GUID/revision, value/unit and qualifier. This illustrative stored shape omits unrelated optional fields:

~~~json
{
  "id": "22222222-2222-4222-8222-222222222222",
  "tankId": "11111111-1111-4111-8111-111111111111",
  "measuredAt": "2026-10-20T09:00:00Z",
  "recordedAt": "2026-10-20T09:01:00Z",
  "revision": 1,
  "readings": [
    {
      "parameterDefinitionId": "9a3594f5-d73f-433e-80cb-5934049c096a",
      "definitionRevision": 1,
      "value": 12.5,
      "unitCode": "mg/L",
      "qualifier": "exact"
    }
  ]
}
~~~

Names/chemical strings are not primary identities. UI fetches tank definitions from Aquarium for entry; Tracking fetches authoritative rules in one batch before accepting a new panel. Snapshot fields such as parameterName/parameterCode/analyteBasis on each stored reading remain an optional unapproved proposal; no such fields are added to the accepted input contract. /tankId is accepted under ADR-005, in Tracking-owned containers within shared ReferenceProjects (ADR-024).

## Accepted profile preference and minimum tank contract — 21 October 2026

PROFILE-01/TANK-01: Aquarium owns required profile measurement preference (Metric, US customary, UK imperial) and minimum tank contract. No default; registration completion gates tank creation/measurement entry. Explicit volume units, authoritative quantities and reviewed conversions prevent reinterpretation/drift on preference changes. Parameter definitions retain independent scientific unit rules. See [accepted contract](../api/tank-and-profile-contract.md) for required fields, server ownership and validation. Advice captures the preference per request; history is immutable.

## Initial parameter catalogue and selection — accepted 21 October 2026

MEAS-05: Stage 2 offers pH, ammonia, nitrite, nitrate, phosphate, calcium, magnesium and alkalinity. Owner explicitly selects tank definitions; Freshwater/Marine does not silently restrict the catalogue. At least one selection is required before recording a panel. Each panel may contain any non-empty subset of selected parameters; testing every selected parameter is not mandatory. Custom definition creation remains Stage 3. Aquarium owns versioned allowed units/input rules; distinguish invalid input from unusual readings and do not reject merely outside a recommended aquarium range. Exact units/analyte basis and executable rule settings remain separate contract work. No catalogue seed or application behaviour implemented. Authority: [ADR-023](../architecture/decisions/adr-023.md).

## Explicit measurement units and reporting basis — accepted 21 October 2026

MEAS-06: every seeded parameter definition explicitly specifies measured quantity, chemical reporting basis, allowed units, display label and validation rules (numeric format, permitted units and applicable bounds). No ambiguous generic ppm unit. Where reporting basis differs, use separate definition variants, especially for ammonia; the initial eight catalogue names are measurement families, not a restriction to exactly eight scientific definitions. Do not conflate total/free ammonia or elemental/compound reporting bases.

Preserve entered value and unit. Initially chart matching definitions/units together; defer automatic cross-basis conversions until reviewed. Scientific units remain independent of Metric/US customary/UK imperial profile preference. Exact seed variants, unit codes, numeric bounds/precision and executable schemas remain contract-readiness work; this approval does not assert those concrete scientific rules have been reviewed. No seed data, conversion engine or application code implemented.

## Measurement-panel contract — accepted 21 October 2026

MEAS-07: measurement-panel submission identifies the tank in the route and checks ownership server-side. Require one offset-bearing measuredAt for the panel; backdating allowed; reject times more than five minutes ahead of server time. readings contains 1–50 entries, no duplicate parameterDefinitionId. Each entry requires definition GUID, positive definition revision, numeric value, explicit unitCode and qualifier (exact, belowDetectionLimit, aboveDetectionLimit). For detection-limit qualifiers the numeric value is the limit, not an exact measurement. Optional panel testMethod max 200 characters and notes max 4,000 characters.

Require an idempotency key: same authorised submission retry returns the original outcome without another panel. Conflicting payload follows the existing conflict policy. Server generates panel ID, recordedAt UTC and revision. Validate the complete panel through the accepted single Aquarium batch and local rules before atomic panel/idempotency/outbox persistence in the same Cosmos container/partition. No partial save. Profile completion, selected-definition eligibility and accepted explicit-unit/basis rules still apply. Exact executable schemas/error extensions and numeric precision/seed rules remain readiness work; no code or test execution performed.

## Definition consistency — accepted 21 October 2026

MEAS-09: Aquarium validation is the definition-consistency point for a new panel. Aquarium validates submitted revisions and returns authoritative rules; Tracking applies those rules and persists exact definition IDs/revisions with the panel. A definition change after successful validation does not invalidate that accepted panel; the next new submission uses then-current definitions. Retain historical definition revisions so saved readings remain interpretable. A stale revision detected during validation returns the accepted 409 with input preservation.

No second Aquarium validation call or distributed SQL/Cosmos transaction is introduced. This consistency rule is limited to definition changes; it does not waive token validation or tank-ownership checks. Existing fail-closed dependency behaviour and same-container/partition local atomicity remain. Timing/retirement scenarios must be verified; no executable behaviour changed.
