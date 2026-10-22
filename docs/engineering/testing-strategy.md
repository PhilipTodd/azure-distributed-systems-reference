# Accepted testing strategy

Version: 0.15 | Date: 21 October 2026 | Status: Accepted approach; implementation and exact tooling pending

Authority: [ADR-030](../architecture/decisions/adr-030.md) and TEST-01/02 in the [approval record](authorised-decisions-2026-10-20.md).

## Verification layers

| Layer | Purpose |
| --- | --- |
| Unit | Deterministic Domain/Application behaviour without Azure dependencies; xUnit for backend, Vitest for frontend |
| Component | Angular TestBed with Vitest for component behaviour |
| Integration | Real persistence behaviour, local transactions/outboxes, messaging and service collaboration; use approved dev Azure where local substitutes cannot establish cloud behaviour |
| Contract | API/event schema validation and compatibility |
| Security | Invalid tokens, cross-owner access, forged actor context and insufficient permissions |
| End-to-end | Small set of critical user journeys plus meaningful failure/retry scenarios |

Use meaningful tests for changed behaviour and risk. AI evaluation gates are added in the AI stage. Backend assertion-library selection/licensing remains open.

## Browser tests

Use Playwright Test with TypeScript. Run a small Chromium suite on pull requests covering tank creation, measurement recording and history viewing as those features arrive. Run broader Firefox and WebKit checks before releases. Use synthetic data and controlled test accounts against Local or approved Development; this does not require a dedicated Test environment.

Keep generated authentication state out of source control. Protect reports, traces and screenshots that may contain user or authentication information. Pin compatible test-runner/browser versions and provision CI dependencies when establishing runnable projects.

Playwright complements Vitest/TestBed. See official [best practices](https://playwright.dev/docs/best-practices) and [browser support](https://playwright.dev/docs/browsers).

## Pull-request gates

Applicable build, static analysis and tests must pass before merge. Failed required checks block merge; report skipped or unavailable checks and the missing evidence honestly. Verification is proportionate: docs-only changes need document checks, while affected executable behaviour needs relevant tests.

There is no blanket coverage percentage initially. Coverage informs review but does not substitute for meaningful assertions. Exact workflow/check names, commands, repository enforcement, fixtures and evidence retention/access settings remain to configure. No checks, pipelines or application tests are implemented by accepting this strategy.

## Customer identity isolation cases

Accepted ID-08/[ADR-009](../architecture/decisions/adr-009.md): in the same browser profile, keep a personal Microsoft session active and register/sign in to Parameter Pilot with the same email address. Verify the distinct customer identity, expected sign-out/switch-account behaviour, unrelated issuer/audience rejection at gateway and APIs, and no email-based account merging or tank access. Include existing customer-session SSO behaviour; do not assume a fresh code on every visit. Use controlled synthetic accounts; these tests have not yet run.

## Customer session cases

ID-10/[ADR-009](../architecture/decisions/adr-009.md): verify supported MSAL localStorage caching across refresh/tabs/browser restart, token renewal and interaction-required fallback. Test logout/account-switch propagation to other open tabs and no stale private data exposure. Keep unsaved measurement input in memory for same-user reauthentication; clear for different-user sign-in or explicit sign-out. Do not assume local cache removal invalidates issued tokens or ends all identity sessions. Browser restoration/provider cookies require real-browser checks. These tests have not run.

## API permission cases

ID-11/[ADR-009](../architecture/decisions/adr-009.md): verify each route's required delegated permission at APIM and the API, read-only mutation denial, wrong-service audience rejection and cross-owner denial even with a valid write scope. Confirm legitimate owned-tank access with the applicable scope. Do not assume Write includes Read or that managed identities confer delegated user authority. Exact route/scope fixture configuration remains pending.

## Synchronous OBO cases

ID-12/[ADR-009](../architecture/decisions/adr-009.md): verify token exchange, expected stable user mapping, downstream audience/scopes/caller restrictions and tank access. Reject Tracking-audience tokens at Aquarium, missing permissions/unapproved callers and forged actor inputs. Exchange/dependency failure must not save a new panel/outbox; preserve UI input for retry. Validate the actual External ID registrations and supported client-authentication setup. No tests have run.

## Worker actor-context cases

ID-13/[ADR-009](../architecture/decisions/adr-009.md): verify authorised job/outbox creation, restricted senders, forged/mismatched job/actor/tank references, owner-only job reads, managed-identity authentication, current-access/entitlement denials and independent result authorisation. Temporary Aquarium outage leaves jobs recoverable without protected work; revocation stops protected processing. Already-committed event relay continues without repeating the original customer write authorisation. Verify no bearer tokens persisted. Tests/configuration remain pending.

## Internal workload boundary cases

ID-14/[ADR-009](../architecture/decisions/adr-009.md): verify approved/unapproved workload callers, missing operation permission, forged actor/tank/action context and cross-owner requests. Customer tokens cannot substitute for workload permissions; workload tokens cannot bypass customer delegation. Verify network restrictions and independent token checks; API-025 remains OBO. Exact fixtures/test execution pending.

## API performance verification

PERF-01/[NFR-002](../requirements/non-functional-requirements.md): measure standard reads/writes separately through APIM, including normal authorisation, Aquarium validation and commit, against 750 ms p95 under agreed representative load. Report cold starts, dependency failures and counts separately; exclude interactive sign-in, uploads and async AI/image execution. Do not use direct-backend timings as gateway-to-response evidence. Load profile, harness and execution evidence remain pending.

## Accepted profile preference and minimum tank contract — 21 October 2026

PROFILE-01/TANK-01: verify no preselected measurement preference, server-side incomplete-profile gating, all three volume systems, explicit unit conversions with no drift across preference changes, name/type/timezone/volume validation, trusted owner and server IDs/timestamps. Advice-stage tests verify preference snapshots and unchanged historical/in-flight advice context after profile changes. [Contract](../api/tank-and-profile-contract.md); tests not executed.

## Initial parameter catalogue and selection — accepted 21 October 2026

MEAS-05: Stage 2 offers pH, ammonia, nitrite, nitrate, phosphate, calcium, magnesium and alkalinity. Owner explicitly selects tank definitions; Freshwater/Marine does not silently restrict the catalogue. At least one selection is required before recording a panel. Each panel may contain any non-empty subset of selected parameters; testing every selected parameter is not mandatory. Custom definition creation remains Stage 3. Aquarium owns versioned allowed units/input rules; distinguish invalid input from unusual readings and do not reject merely outside a recommended aquarium range. Exact units/analyte basis and executable rule settings remain separate contract work. No catalogue seed or application behaviour implemented. Verify empty-selection/panel rejection, permitted subsets, unselected-definition denial, access isolation and acceptance of unusual but valid readings. Tests pending. Authority: [ADR-023](../architecture/decisions/adr-023.md).

## Explicit measurement units and reporting basis — accepted 21 October 2026

MEAS-06: every seeded parameter definition explicitly specifies measured quantity, chemical reporting basis, allowed units, display label and validation rules (numeric format, permitted units and applicable bounds). No ambiguous generic ppm unit. Where reporting basis differs, use separate definition variants, especially for ammonia; the initial eight catalogue names are measurement families, not a restriction to exactly eight scientific definitions. Do not conflate total/free ammonia or elemental/compound reporting bases.

Preserve entered value and unit. Initially chart matching definitions/units together; defer automatic cross-basis conversions until reviewed. Scientific units remain independent of Metric/US customary/UK imperial profile preference. Exact seed variants, unit codes, numeric bounds/precision and executable schemas remain contract-readiness work; this approval does not assert those concrete scientific rules have been reviewed. No seed data, conversion engine or application code implemented. Verify basis/unit labels, unsupported-unit denial, variant separation, preservation of entered quantities and no silent mixing/conversion in charts. Tests pending.

## Measurement-panel contract — accepted 21 October 2026

MEAS-07: measurement-panel submission identifies the tank in the route and checks ownership server-side. Require one offset-bearing measuredAt for the panel; backdating allowed; reject times more than five minutes ahead of server time. readings contains 1–50 entries, no duplicate parameterDefinitionId. Each entry requires definition GUID, positive definition revision, numeric value, explicit unitCode and qualifier (exact, belowDetectionLimit, aboveDetectionLimit). For detection-limit qualifiers the numeric value is the limit, not an exact measurement. Optional panel testMethod max 200 characters and notes max 4,000 characters.

Require an idempotency key: same authorised submission retry returns the original outcome without another panel. Conflicting payload follows the existing conflict policy. Server generates panel ID, recordedAt UTC and revision. Validate the complete panel through the accepted single Aquarium batch and local rules before atomic panel/idempotency/outbox persistence in the same Cosmos container/partition. No partial save. Profile completion, selected-definition eligibility and accepted explicit-unit/basis rules still apply. Exact executable schemas/error extensions and numeric precision/seed rules remain readiness work; no code or test execution performed. Verify 1/50-entry boundaries, duplicates, required fields/qualifiers, offset timestamps, backdating, exactly-five-minute versus beyond-tolerance times with controlled clock, text limits, mixed valid/invalid panel no-save and same-key retry/conflict behaviour. Tests pending.

## Submission errors and input preservation — accepted 21 October 2026

MEAS-08: use consistent safe error bodies with stable code, explanation, trace ID and field details where applicable. Accepted mappings: 400 malformed request; 401 missing/expired authentication; 403 missing API permission; 404 absent/inaccessible tank without owner disclosure; 409 stale definition revision or idempotency-key payload conflict (distinct codes); 422 invalid readings/time; 503 temporary Aquarium/OBO unavailability. Only temporary OBO/dependency availability failures map to 503; actual authentication/permission failures retain their appropriate 401/403 semantics. Invalid or unusable trusted dependency responses fail closed without claiming a saved panel.

UI retains input for same-user reauthentication/retry, subject to ID-10 clearing on account change/sign-out. Refresh stale definitions while preserving entered values for review; never auto-resubmit after rules change. Field validation saves nothing. Permission/inaccessible-tank responses explain failure safely without exposing neighbour data. Do not expose tokens, internal exceptions or private dependency payloads. Rate-limit and unexpected-error conventions remain applicable; the table is not an exhaustive HTTP contract. No application changes or executable schema validation performed. Verify each mapping, safe error details, field targeting, no partial save, distinct conflict codes, stale-rule review without automatic resubmission and no input transfer across users. Tests pending.

## Minimum Stage 2 Local setup — accepted 21 October 2026

DEV-03: minimum Stage 2 Local setup runs Angular UI and Aquarium/Tracking APIs directly through development tooling. Docker Compose starts SQL Server Developer and Cosmos DB NoSQL emulator containers; use a small repeatable synthetic seed set. Actual Development External ID supports customer authentication/OBO. Select/pin supported compatible container/tool versions after verification; no preview assumption or floating latest pin. Local certificate and secrets follow ID-15/ADR-027.

Emulator/container results are not proof of Azure parity. Verify required operation support, including same-container/partition transactions, and real Development identity/permissions/cloud behaviour. If a required operation is unsupported locally, use the approved Development dependency for that check rather than building an inaccurate substitute. No unapproved resource creation/spend implied.

Advisor/PostgreSQL/photo dependencies wait for their stages. Add Service Bus and workers when the authorised implementation slice requires them; preserve core synchronous transaction/outbox design and do not fabricate broker-delivery evidence. Docker Compose manages dependencies, not a requirement to containerise local UI/APIs. No Compose file, dependencies, seeds, projects or resources created in this documentation update.

## Definition consistency — accepted 21 October 2026

MEAS-09: Aquarium validation is the definition-consistency point for a new panel. Aquarium validates submitted revisions and returns authoritative rules; Tracking applies those rules and persists exact definition IDs/revisions with the panel. A definition change after successful validation does not invalidate that accepted panel; the next new submission uses then-current definitions. Retain historical definition revisions so saved readings remain interpretable. A stale revision detected during validation returns the accepted 409 with input preservation.

No second Aquarium validation call or distributed SQL/Cosmos transaction is introduced. This consistency rule is limited to definition changes; it does not waive token validation or tank-ownership checks. Existing fail-closed dependency behaviour and same-container/partition local atomicity remain. Timing/retirement scenarios must be verified; no executable behaviour changed. Verify stale-at-check rejection, rule change after successful check followed by persistence with validated revisions, and next new submission using current revisions. Do not infer idempotency replay requires validation against newer rules. Test evidence pending.
