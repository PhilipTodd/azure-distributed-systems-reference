# Domain model and invariants

Version: 0.2 | Date: 19 October 2026 | Status: Draft

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
- Backdating is allowed; future tolerance remains TBD.
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
