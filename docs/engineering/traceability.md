# Traceability register

Version: 0.33 | Date: 21 October 2026 | Status: Draft

Requirement -> story -> design/ADR -> API/event/data contract -> issue -> implementation -> tests/evaluations -> PR -> human approval.

| Requirement | Story | Design | Contract | Verification |
| --- | --- | --- | --- | --- |
| FR-002, NFR-007 | US-007 | ADR-001, ADR-009 | API-001–003 | Lifecycle/owner isolation |
| FR-003–004, NFR-004 | US-001–002 | ADR-004–007 | API-005–008, EVT-003–005 | Units, retries, concurrency, broker outage |
| FR-005–008 | US-003–004 | Domain/time rules | API-006, API-009–012 | Ordering/timezone/completion retries |
| FR-011/014 | US-005 | ADR-014–015; DEC-07–09 | API-017–019/024 | Grounding/isolation/quota/failure; immutable history snapshot; no photo context |
| FR-010 | US-006 | Accepted ADR-016; DEC-04–06 | API-014/016, EVT-007–008; API-015 withdrawn | Actual-byte cap, partial upload, crop/pad WebP, retained original, unsafe/orphan cleanup |
| FR-012–013 | Commercial stories TBD | ADR-010/019–020 | API-020–021; accounting TBD | Signature/order/dedup/reconciliation |
| NFR-006 | US-008 | Recovery plan | Data/runbooks | Restore exercise |

FR-009 dosing and FR-015 export/delete need expanded stories/contracts before implementation. NFR targets link to release verification plans when environments exist. Issues, source/test files, PRs and approval references are intentionally unset. Do not manufacture evidence.

Audit record: task/agent identity, requirements, rationale, checks, compatibility, security/telemetry impact, docs/traceability, reviewer and outcome. Private model reasoning is not an audit artefact.

## Accepted async traceability — 20 October 2026

| Requirements | Decision | Model/contract | Verification |
| --- | --- | --- | --- |
| FR-002–008 / NFR-004 | ADR-007 | RecordParameter; owner state/outbox | Durable write during broker outage; duplicate relay |
| FR-010 | ADR-012/016 | Tracking worker; ProcessPhoto queue | Crop/pad, retry/lease, safe completion |
| FR-011 | ADR-003/012 | Advisor worker and owner context APIs | Isolation, durable job, model failure |
| NFR-007/012 | ADR-008/012/022 | One namespace; scoped entities/shared plan | Fan-out vs competing consumers; identity/capacity |
| NFR-009 | ADR-017 partial | Direct telemetry with message context | Safe tracing without business-log queue |

[Approval evidence](authorised-decisions-2026-10-20.md). Implementation/test/PR links remain unset.

## Measurement definition/panel traceability

FR-002/003/004 -> US-009 -> accepted ADR-023/ADR-003 -> API-004/005/025 -> Aquarium definition revisions and Tracking panel -> verification for batched retrieval, all-or-nothing rules, stale revision, owner isolation, dependency failure/retry and unchanged asynchronous outbox publication. Exact implementation/test/PR references are pending.

## Shared placement and partition traceability

FR-002/003, NFR-003/004/007/012 -> accepted ADR-005/024 -> Aquarium schema and Tracking containers in platform-owned databases -> verify schema-scoped runtime/migration permissions, container-scoped Tracking roles, same-container transactional batch, cross-owner denial, growth/hotspots, shared capacity and restore reconciliation. Implementation/verification evidence remains pending.

## Environment and platform readiness traceability

ENV-01/02 -> ADR-025 -> Local/dev setup and initial delivery targets -> repeatable automated tests, synthetic data and dev-only permissions -> release gate for deferred Test/Production. PLATFORM-01/02 -> ADR-024 -> external platform handover/resource IDs/scopes/capacity/isolation verification before app agentic implementation. Completion evidence pending; acceptance alone does not mark Stage 1 done.

## CI/CD authority traceability

CI-01–03 -> accepted ADR-018 -> PR/build/security/ACR/OIDC/dev-deploy workflow design -> verify protected checks, untrusted PR isolation, scoped access, image identity, dev smoke/recovery and noncompeting cutover -> legacy retirement evidence. Implementation/workflow/PR links remain pending; platform pipeline excluded.

## Identity traceability

ID-01–05 -> accepted ADR-009 -> FR-001/002 and all protected API/worker jobs -> APIM/API token checks, Aquarium user/access decisions, Tracking batch, trusted managed-identity/actor propagation -> negative token/bypass/cross-owner/forged-context/outage tests and stable mapping across email changes. Real configuration/test/PR evidence pending.

## Hosting/ingress/configuration traceability

HOST-01 -> ADR-011 -> separate API apps/shared plan -> compatibility/load/identity checks. NET-01/02 -> ADR-026 -> APIM-only browser API path -> direct-call denial, approved workload access and invalid-token/role rejection. CONFIG-01/02 -> ADR-027 -> App Configuration/Key Vault/local settings -> allowed/denied reads, no source/browser/log secret leakage and later refresh/rotation tests. Settings and implementation/test evidence remain pending.

## Configuration access isolation traceability

CONFIG-03/04 -> accepted ADR-027 -> service API/worker access matrix and separate deployment principal -> required reads succeed; cross-service settings/secrets denied except explicitly shared nonsecrets; runtime administration denied; deployment management bounded; shared-store isolation verified or separate-store proposal raised. NFR-007/009; concrete roles, tests and implementation evidence pending.

## Operational/technology baseline traceability

CONFIG-05–07 -> ADR-027 -> config/rotation/readiness policy -> missing required configuration not Ready, bounded retry, loaded-config continuity only with valid authorisation, restart/rotation proof and retryable jobs. DEV-01–02 -> ADR-029 -> Local setup -> individual scoped login/emulator-cloud parity/fresh setup tests. ENG-01 -> ADR-002 -> dependency rules/API-worker reuse -> architecture review/checks. TECH-01–03 -> ADR-028 -> compatibility/pinning matrix -> actual builds/tests once runnable projects exist. No test execution or installation evidence invented.

## Testing decision traceability

TEST-01/02 -> accepted ADR-030 -> testing strategy/standards/delivery/Definition of Done -> risk-based tests, required passing applicable PR checks, xUnit/Vitest/TestBed/Playwright, Chromium PR and broader pre-release browser checks. Actual workflow runs, fixtures, security negatives and protected report evidence remain pending.

## Customer account-isolation traceability

ID-06–08 -> accepted ADR-009 -> FR-001/002 and security/testing strategy -> dedicated customer authority/local email passcodes, deferred federation, stable identity mapping and visible switch-account -> same-browser/same-email Microsoft coexistence, wrong-issuer/audience rejection and no email-based merging/cross-owner access. [Approval](authorised-decisions-2026-10-21.md); configuration and execution evidence pending.

## Customer MFA sequencing traceability

ID-09 -> ADR-009/security -> Stages 1–5 email-passcode authentication without mandatory customer MFA -> Stage 6 explicit requirements/launch gate for MFA, recovery and billing changes. Earlier reassessment on material risk change; separate administrative protections. Policy acceptance is not tenant configuration evidence.

## Customer session traceability

ID-10 -> ADR-009/security -> MSAL Angular/localStorage -> refresh/multi-tab/return experience, renewal/interactive fallback, logout/account switching and same-user draft recovery -> browser/security tests without stale cross-account data. [Approval](authorised-decisions-2026-10-21.md); implementation evidence pending.

## API permission traceability

ID-11 -> ADR-009/security -> separate customer read/write permissions per service plus Aquarium-authoritative tank checks -> route/scope tests, wrong-audience/insufficient-scope/read-only mutation/cross-owner denial. [Approval](authorised-decisions-2026-10-21.md); exact identifiers and execution evidence pending.

## Synchronous delegation refinement

ID-12 -> ADR-009/API-025 -> Tracking OBO exchange and Aquarium delegated-token/tank checks -> audience/scope/caller/ownership and exchange-failure tests. [Approval](authorised-decisions-2026-10-21.md); executable configuration/test evidence pending.

## Worker context traceability

ID-13 -> ADR-009/async processing -> authorised service-owned job/outbox + managed-identity worker -> forged context/sender/access revocation/dependency-outage/result-access tests. Committed fact relay does not reauthorise the original write. [Approval](authorised-decisions-2026-10-21.md); implementation evidence pending.

## Internal workload API traceability

ID-14 -> ADR-009/security/API catalogue -> dedicated access/entitlement and later Advisor-history contracts -> caller/permission/actor/tank/action/network denial tests. API-025 remains OBO. [Approval](authorised-decisions-2026-10-21.md); detailed contracts/verification pending.

## Observability baseline traceability

OBS-01 -> ADR-017/observability -> API/worker OpenTelemetry, safe structured logs and latency/failure/dependency/outbox/queue/DLQ metrics -> correlated HTTP/outbox/message diagnostics, safe-field review and negative secret/private-payload logging checks. [Approval](authorised-decisions-2026-10-21.md); instrumentation and execution evidence pending.

## Diagnostic policy traceability

OBS-02 -> ADR-017/observability -> supported 30-day retention target, full initial traces and controlled log levels -> table-policy/exporter checks, trace correlation, noise/failure visibility and pre-load-test volume review. [Approval](authorised-decisions-2026-10-21.md); configuration/measurement evidence pending.

## Alert ownership traceability

OBS-03 -> ADR-017/observability/runbooks -> owner-designated email, grouped notifications/safe links/recovery messages -> controlled alert-delivery and recovery verification when authorised. Best-effort Development response; public support reviewed before Stage 4 launch. [Approval](authorised-decisions-2026-10-21.md); destination/configuration evidence pending.

## Development alert thresholds — accepted 21 October 2026

OBS-04 -> ADR-017/observability/runbooks -> initial failure/backlog triggers -> controlled threshold crossings, validation/access-denial exclusions, recovery/dedup notifications and manual DLQ investigation. [Approval](authorised-decisions-2026-10-21.md); actual alert/query/delivery tests pending.

## API latency traceability

PERF-01 -> NFR-002 -> gateway-to-response read/write latency including normal dependencies -> representative-load p95 checks, with separate cold-start/failure reporting. [Approval](authorised-decisions-2026-10-21.md); agreed load/harness and measured evidence pending.

## Stage 2 identity configuration — accepted 21 October 2026

ID-15 -> ADR-009/security/Local setup/API-025 -> three registrations, own audiences, scope names, tid + oid stable mapping and certificate-authenticated restricted Tracking OBO -> real registration/token/claim/permission/ownership tests. [Approval](authorised-decisions-2026-10-21.md); setup evidence pending.

## Accepted profile preference and minimum tank contract — 21 October 2026

PROFILE-01/TANK-01 -> FR-001/002/003 and later FR-011 -> Aquarium profile/tank contract and API-025 completed-profile eligibility -> onboarding/owner/unit/conversion/validation tests and later immutable advice preference tests. [Approval](authorised-decisions-2026-10-21.md); executable schemas and test evidence pending.

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

## Minimum Stage 2 Local setup — accepted 21 October 2026

DEV-03: minimum Stage 2 Local setup runs Angular UI and Aquarium/Tracking APIs directly through development tooling. Docker Compose starts SQL Server Developer and Cosmos DB NoSQL emulator containers; use a small repeatable synthetic seed set. Actual Development External ID supports customer authentication/OBO. Select/pin supported compatible container/tool versions after verification; no preview assumption or floating latest pin. Local certificate and secrets follow ID-15/ADR-027.

Emulator/container results are not proof of Azure parity. Verify required operation support, including same-container/partition transactions, and real Development identity/permissions/cloud behaviour. If a required operation is unsupported locally, use the approved Development dependency for that check rather than building an inaccurate substitute. No unapproved resource creation/spend implied.

Advisor/PostgreSQL/photo dependencies wait for their stages. Add Service Bus and workers when the authorised implementation slice requires them; preserve core synchronous transaction/outbox design and do not fabricate broker-delivery evidence. Docker Compose manages dependencies, not a requirement to containerise local UI/APIs. No Compose file, dependencies, seeds, projects or resources created in this documentation update.

## Definition consistency — accepted 21 October 2026

MEAS-09: Aquarium validation is the definition-consistency point for a new panel. Aquarium validates submitted revisions and returns authoritative rules; Tracking applies those rules and persists exact definition IDs/revisions with the panel. A definition change after successful validation does not invalidate that accepted panel; the next new submission uses then-current definitions. Retain historical definition revisions so saved readings remain interpretable. A stale revision detected during validation returns the accepted 409 with input preservation.

No second Aquarium validation call or distributed SQL/Cosmos transaction is introduced. This consistency rule is limited to definition changes; it does not waive token validation or tank-ownership checks. Existing fail-closed dependency behaviour and same-container/partition local atomicity remain. Timing/retirement scenarios must be verified; no executable behaviour changed.

## Readiness preparation traceability

READY-01 -> accepted design/ADR-009/023/029 and tank/profile contract -> concrete dependency/configuration/API/seed specification -> compatibility/schema review, scientific seed approval, platform handover and reproducible baseline checks -> human Stage 1 completion review and separate Stage 2 implementation authorisation. [Approval](authorised-decisions-2026-10-21.md). Specification and evidence not yet produced by this update.
