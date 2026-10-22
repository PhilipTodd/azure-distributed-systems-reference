# Aquarium parameter definitions and batched panel validation

Version: 0.10 | Date: 21 October 2026 | Status: Accepted interaction; detailed HTTP/schema contract Draft

Authority: [ADR-023](../architecture/decisions/adr-023.md).

## UI definition discovery

API-004: GET /api/v1/tanks/{tankId}/parameter-definitions returns the owner-authorised tank-selected definitions, stable GUIDs, current revisions, allowed units, qualifiers and relevant input rules for entry. Rule values/response schema remain draft. UI validation aids usability; Tracking must independently use trusted Aquarium information.

## Internal batch interaction — API-025

Proposed route: POST /internal/v1/tanks/{tankId}/measurement-validation-context. Exact route/schema is not separately approved; acceptance is of one batched direct call per new panel submission.

Tracking uses OAuth OBO to obtain an Aquarium-specific delegated token for the validated customer request and supplies tank context plus all distinct submitted parameterDefinitionId/definitionRevision pairs. No private notes or reading values need to be sent merely to retrieve rules.

Aquarium validates caller authority, tank access and tank-selected active definitions. A successful response contains authoritative IDs/current revisions, quantity/analyte basis, allowed units/conversions and input rules. Tracking checks submitted revisions and applies the returned rules to every reading.

The batch is all-or-nothing for eligibility: missing/retired/unselected/unknown entries cannot yield a silently partial accepted panel. Do not issue one request per reading or query Aquarium SQL from Tracking.

## Tracking outcomes — accepted MEAS-08 mapping

| Condition | Proposed outcome |
| --- | --- |
| Valid panel and successful Cosmos transaction | 201; persisted panel and local outbox |
| Stale definition revision | 409, code parameter-definition-revision-stale; refresh UI configuration without discarding input |
| Invalid/unselected/retired definition or incompatible value/unit | 422 with per-reading validation errors |
| Invalid/missing authentication | 401 |
| Missing applicable API permission | 403 |
| Tank unavailable to actor | 404; no cross-owner disclosure |
| Aquarium unavailable, timed out or response unusable | 503, code measurement-validation-unavailable; no panel/outbox written |
| Conflicting idempotency payload | 409 under existing conventions |

These mappings are accepted under MEAS-08; full executable error schemas still need validation before implementation. Fail-closed behaviour, actionable revision rejection and input preservation are accepted. Do not turn a dependency outage into a saved/queued measurement acceptance. Idempotency replay follows existing API conventions.

## Availability and consistency

Use bounded call timeout/retry settings, still TBD. No initial cache/projection bypass. Preserve definition revisions in Aquarium and IDs/revisions in Tracking; name strings are not identities. A future local projection needs explicit freshness, revocation and version reconciliation.

Validation observes an authorised definition version at call time, not a global SQL/Cosmos transaction. MEAS-09 below accepts validation-time definition consistency for changes between that check and local commit. Cosmos /tankId is now Accepted under ADR-005, with Tracking containers in shared ReferenceProjects (ADR-024); optional per-reading definition display snapshot remains Proposed.

## Accepted OBO authentication refinement

ID-12/[ADR-009](../architecture/decisions/adr-009.md): the synchronous panel-validation call uses OBO and an Aquarium-audience delegated access token. Aquarium validates user/delegated permission, permitted calling application and tank access. The incoming Tracking token is not forwarded as Aquarium authentication. Exact registration/consent/client authentication/permission details remain to verify. Exchange failure fails closed; UI retains input and no new panel/outbox is saved. HTTP mapping remains Draft.

## Stage 2 identity configuration — accepted 21 October 2026

ID-15/[ADR-009](../architecture/decisions/adr-009.md): API-025 requires Aquarium-audience OBO delegation with Aquarium.Read, only the approved Tracking calling application, and current tank ownership. Map validated tid + oid to the internal Aquarium user. Tracking uses registered certificate confidential-client authentication for the exchange. Registration GUIDs/full scope identifiers/certificate references and schemas remain setup work. No grants configured.

## Accepted profile preference and minimum tank contract — 21 October 2026

PROFILE-01: include completed required profile in authoritative eligibility for measurement entry within the existing once-per-panel Aquarium batch. Incomplete profile denies new panel/outbox creation; UI directs owner to complete the explicit measurement preference. No default and no extra per-reading/per-panel profile call. Exact response/error schema remains to define. [Profile contract](tank-and-profile-contract.md).

## Initial parameter catalogue and selection — accepted 21 October 2026

MEAS-05: Stage 2 offers pH, ammonia, nitrite, nitrate, phosphate, calcium, magnesium and alkalinity. Owner explicitly selects tank definitions; Freshwater/Marine does not silently restrict the catalogue. At least one selection is required before recording a panel. Each panel may contain any non-empty subset of selected parameters; testing every selected parameter is not mandatory. Custom definition creation remains Stage 3. Aquarium owns versioned allowed units/input rules; distinguish invalid input from unusual readings and do not reject merely outside a recommended aquarium range. Exact units/analyte basis and executable rule settings remain separate contract work. No catalogue seed or application behaviour implemented. Authority: [ADR-023](../architecture/decisions/adr-023.md).

## Explicit measurement units and reporting basis — accepted 21 October 2026

MEAS-06: every seeded parameter definition explicitly specifies measured quantity, chemical reporting basis, allowed units, display label and validation rules (numeric format, permitted units and applicable bounds). No ambiguous generic ppm unit. Where reporting basis differs, use separate definition variants, especially for ammonia; the initial eight catalogue names are measurement families, not a restriction to exactly eight scientific definitions. Do not conflate total/free ammonia or elemental/compound reporting bases.

Preserve entered value and unit. Initially chart matching definitions/units together; defer automatic cross-basis conversions until reviewed. Scientific units remain independent of Metric/US customary/UK imperial profile preference. Exact seed variants, unit codes, numeric bounds/precision and executable schemas remain contract-readiness work; this approval does not assert those concrete scientific rules have been reviewed. No seed data, conversion engine or application code implemented.

## Measurement-panel contract — accepted 21 October 2026

MEAS-07: measurement-panel submission identifies the tank in the route and checks ownership server-side. Require one offset-bearing measuredAt for the panel; backdating allowed; reject times more than five minutes ahead of server time. readings contains 1–50 entries, no duplicate parameterDefinitionId. Each entry requires definition GUID, positive definition revision, numeric value, explicit unitCode and qualifier (exact, belowDetectionLimit, aboveDetectionLimit). For detection-limit qualifiers the numeric value is the limit, not an exact measurement. Optional panel testMethod max 200 characters and notes max 4,000 characters.

Require an idempotency key: same authorised submission retry returns the original outcome without another panel. Conflicting payload follows the existing conflict policy. Server generates panel ID, recordedAt UTC and revision. Validate the complete panel through the accepted single Aquarium batch and local rules before atomic panel/idempotency/outbox persistence in the same Cosmos container/partition. No partial save. Profile completion, selected-definition eligibility and accepted explicit-unit/basis rules still apply. Exact executable schemas/error extensions and numeric precision/seed rules remain readiness work; no code or test execution performed.

## Submission errors and input preservation — accepted 21 October 2026

MEAS-08: use consistent safe error bodies with stable code, explanation, trace ID and field details where applicable. Accepted mappings: 400 malformed request; 401 missing/expired authentication; 403 missing API permission; 404 absent/inaccessible tank without owner disclosure; 409 stale definition revision or idempotency-key payload conflict (distinct codes); 422 invalid readings/time; 503 temporary Aquarium/OBO unavailability. Only temporary OBO/dependency availability failures map to 503; actual authentication/permission failures retain their appropriate 401/403 semantics. Invalid or unusable trusted dependency responses fail closed without claiming a saved panel.

UI retains input for same-user reauthentication/retry, subject to ID-10 clearing on account change/sign-out. Refresh stale definitions while preserving entered values for review; never auto-resubmit after rules change. Field validation saves nothing. Permission/inaccessible-tank responses explain failure safely without exposing neighbour data. Do not expose tokens, internal exceptions or private dependency payloads. Rate-limit and unexpected-error conventions remain applicable; the table is not an exhaustive HTTP contract. No application changes or executable schema validation performed.

## Definition consistency — accepted 21 October 2026

MEAS-09: Aquarium validation is the definition-consistency point for a new panel. Aquarium validates submitted revisions and returns authoritative rules; Tracking applies those rules and persists exact definition IDs/revisions with the panel. A definition change after successful validation does not invalidate that accepted panel; the next new submission uses then-current definitions. Retain historical definition revisions so saved readings remain interpretable. A stale revision detected during validation returns the accepted 409 with input preservation.

No second Aquarium validation call or distributed SQL/Cosmos transaction is introduced. This consistency rule is limited to definition changes; it does not waive token validation or tank-ownership checks. Existing fail-closed dependency behaviour and same-container/partition local atomicity remain. Timing/retirement scenarios must be verified; no executable behaviour changed.
