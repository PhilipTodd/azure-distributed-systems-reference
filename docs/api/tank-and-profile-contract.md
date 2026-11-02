# Tank and measurement-preference contract

Version: 0.1 | Date: 21 October 2026 | Status: Accepted behaviour; executable schemas pending

Authority: PROFILE-01/TANK-01 in the [approval record](../engineering/authorised-decisions-2026-10-21.md). Aquarium owns the profile and Tank aggregate. No new service/store or C4 topology is introduced.

Candidate executable Profile/ProfileUpdate/TankCreate/Tank/Volume shapes now exist in the [Stage 2 schema bundle](schemas/stage-2.schema.json). Proposed routes, wire enums, decimal/size limits and conversion treatment are in [SPEC-02](../engineering/stage-2-readiness-specification.md#candidate-executable-contracts); these concrete choices were accepted under SPEC-02 in the [29 October record](../engineering/authorised-decisions-2026-10-29.md); runtime verification remains pending.

## Required registration profile completion

After External ID authentication, require an explicit profile choice before tank creation or measurement entry. No preselected measurement-system default. An authenticated user may complete/read their own onboarding profile before this gate is satisfied; authentication alone does not imply completed registration. Enforce the gate server-side, not only in the UI.

Three explicit choices: Metric, US customary and UK imperial. User profile stores the choice; exact enum wire values remain schema work. The profile controls general volume/presentation preferences and future entry. US and UK gallons must be distinguished in labels and unit codes. Do not use an ambiguous gallon unit.

Profile updates affect future presentation/entry and advice requests; they never reinterpret stored numbers or rewrite historical advice. Preserve explicit units and authoritative quantities; convert through reviewed conversions and round for presentation rather than repeatedly rewriting stored values. Parameter definitions retain their own supported units and scientific meaning: pH, salinity, alkalinity and concentration units cannot be inferred from this profile alone. Specific presentation units/precision outside the agreed volume choices remain to define when relevant.

## Minimum tank creation

| Field | Accepted rule |
| --- | --- |
| Name | Required, trimmed, 1–100 characters; duplicate names allowed |
| Water type | Required Freshwater or Marine; reef tanks use Marine |
| Timezone | Required valid IANA timezone; browser suggests, user can change; Australia/Sydney is an example, not a default |
| Estimated operating water volume | Optional positive decimal; enter/display litres, US gallons or UK imperial gallons according to the explicit profile choice; request carries explicit unit |
| Tank ID | Server-generated GUID |
| Owner | Server resolves Aquarium internal user from validated identity; never trusts browser owner ID |
| Created timestamp | Server-generated UTC |

The original litres-only entry proposal is refined by the accepted preference: volume input is not forced to litres. Preserve sufficient quantity/unit information for accurate conversion. Canonical persistence representation, numeric precision/range and exact JSON schema are implementation-contract details to settle before implementation. A future dosing calculation must require suitable volume even though tank creation does not. Livestock/equipment/detail extensions do not block this slice.

Validate required name/type/timezone, optional positive volume and unambiguous unit server-side. Verify incomplete-profile mutation denial, all three choices, owner isolation, volume conversion/display, repeated preference changes without quantity drift, and UTC timestamps. No code or migration was created.

## Advice context and history

When advice is implemented, include the current explicit measurement preference in the Advisor request context and immutable input snapshot together with explicit parameter units. Render new advice in the requested conventions without changing parameter scientific meaning. Changing a profile leaves existing advice text and original context unchanged, including any litre/gallon wording. An in-flight request retains the preference captured for that request. Photos remain excluded from advice context.
