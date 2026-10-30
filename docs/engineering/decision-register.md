# Decision and risk register

Version: 0.35 | Date: 30 October 2026 | Status: Draft

## Stage 2 accepted baseline — 29 October 2026

30 October latest ownership/access direction: [ADR-031](../architecture/decisions/adr-031.md) is accepted with **PP ownership** of exclusive configuration/vault instances and deployment deferred to PP Bicep changes. Earlier platform-owned proposals below are historical. The owner selected a dedicated platform SQL administrators group; [scoped-access setup](../infrastructure/scoped-access-readiness.md) is the next implementation/verification item. No identities/grants/resources were changed by this documentation task.

30 October current direction: the [owner record](authorised-decisions-2026-10-30.md) retains B1, includes APIM Developer for education and accepts the [revised budget](../infrastructure/development-hosting-budget-2026-10-30.md) of A$118.41/month (approximately A$120/month) total before tax/new variable usage including planned ACR. This supersedes the former A$80 target; later cost optimisation remains possible. B2 and the old incremental allowance remain withdrawn. Proposed ADR-031 isolation, scoped access/retention, ingress verification and later deployment approval remain open; no platform change occurred.

The [readiness specification](stage-2-readiness-specification.md) presents SPEC-01–04: exact dependency/image candidates, concrete contract/limit proposals, 12 scientific seed variants and Local configuration/bootstrap choices. The owner accepted all four recommendations, including scientific seed content, in the [29 October record](authorised-decisions-2026-10-29.md). Structural verification is separate from runtime/platform evidence. This acceptance does not reopen architecture or authorise application implementation, platform deployment/spend or merge.

| Priority | Topic | Position/status | Owner / gate |
| --- | --- | --- | --- |
| High | First release | Tracking, maintenance and charts confirmed | Product owner; recorded chat direction |
| High | Aquarium scope | Accepted: general freshwater/marine tracking | Owner; DEC-03 |
| High | Tank sharing | Accepted: single-owner tanks | Architect; before access contract |
| High | Region | Accepted: Australia East preference; verify support | Platform owner; verify availability |
| High | Budget | Accepted approximately A$120/month whole-portfolio estimate before tax/additional variable usage; B1 plus APIM Developer; later optimisation allowed | Owner; applicable deployment approval and actual-cost review remain |
| High | Free/paid policy | Free tracking/paid AI; pricing/limits TBD | Product owner; before commercial release |
| High | Platform inventory | Source inspected: azure-reference-platform; placement/ownership accepted ADR-024; live resources/capacity/permissions unverified | Platform owner; before IaC approval |
| High | Units/dosing | Reviewed catalogue/formulas required | Domain reviewer; before calculator |
| High | Dependency failure | Accepted ADR-009: fail closed when required authorisation context is unavailable | Architect; detailed dependency/recovery settings TBD |
| High | Recovery | NFR-006 target proposed; tier feasibility unverified | Operations; before production |
| High | AI | Model/region/cost/corpus/data handling TBD | AI owner; before AI approval |
| Medium | Payment | Stripe candidate, not selected | Product owner |
| Medium | Xero | Scope retained; later timing proposed | Product/accounting owner |
| Medium | CI authority | Accepted ADR-018: GitHub Actions sole authority; migrate/retire Azure DevOps after verification | Engineering owner; workflow/cutover evidence pending |
| Medium | Agent surface | Target IDE/cloud configuration TBD | Engineering owner; before activation |
| Medium | Retention/privacy | Policy TBD | Owner; before real user data |
| Medium | Cosmos growth | /tankId Accepted ADR-005; growth/hotspot/query-cost tests still required | Data owner; before production |
| Medium | Versions/licensing | Accepted ADR-028 majors/pinning; exact compatible SDK/provider/tool versions/licensing still unverified | Engineering owner |
| Medium | AI drift | Versioned evaluations/rollback proposed | AI owner |

Roles are accountability placeholders, not appointed people. Accepted decisions require named approver/date/evidence. Only explicitly recorded decisions are accepted; other architectural approval remains pending.

## Accepted changes — 19 October 2026

[Approval record](authorised-decisions-2026-10-19.md) is the evidence for DEC-01–09. ADR-015/016/021 Accepted; ADR-004/022 Partially Accepted.

Photo route: API through Tracking, exact 5,242,880-byte cap; worker WebP crop/pad; retain original. Advice: history list/input snapshots; exclude photos. PostgreSQL consolidates Advisor persistence/retrieval. Remaining photo encoding/alignment/padding/upscaling limits and PostgreSQL sizing/index settings stay TBD.

## Accepted worker decisions — 20 October 2026

Three service-owned Function Apps replace generic processor/standalone photo worker; core writes remain synchronous with local outboxes. One namespace uses separate commands/subscriptions; no common event database or queued tracing. See [approval record](authorised-decisions-2026-10-20.md).

Outstanding foundation checks: shared plan OS/SKU/runtime/Always On, platform permissions/capacity, per-workload concurrency, exact broker entity settings, recovery and scaling/extraction thresholds. Acceptance is architectural, not evidence these resources exist.

## Accepted measurement configuration and validation

MEAS-01–04 accept Aquarium definition/rule ownership, measurement panels, one batched direct validation call and fail-closed/input-preserving behaviour. [ADR-023](../architecture/decisions/adr-023.md) is Accepted; ADR-003 is clarified. /tankId is now Accepted in ADR-005; optional display snapshots, rule values, contract settings and concurrent-update handling remain open. Commercial boundaries are not blanket-approved.

## Shared-platform decisions accepted

ADR-024 accepts shared ownership, Aquarium schema in ReferenceProjectsDb and Tracking containers in ReferenceProjects. ADR-005 accepts /tankId. Platform repository defaults are evidence of definitions, not deployed state; live identity/capacity/hosting verification remains a Stage 1 gate. [Inventory](../infrastructure/platform-inventory.md).

## Accepted environment and platform sequencing

ENV-01/02 and ADR-025 accept Local/dev only; Test/Production provisioning waits for release preparation. Automated tests remain required. PLATFORM-01/02 extend shared hosting ownership and make platform provision/deployment an externally managed prerequisite before app agentic implementation. No request to alter/deploy platform has been made. Numeric NFRs/recovery and concrete identity/network/isolation remain separate decisions. CI/CD authority is subsequently accepted in ADR-018; workflow implementation remains pending.

## CI/CD decision accepted

GitHub Actions sole authority and migration/retirement of Azure DevOps application pipelines accepted under ADR-018. Outstanding Stage 1 evidence: actual workflows, check/ruleset configuration, OIDC permissions, ACR integration, dev deployment approval settings and safe cutover/retirement. Platform pipeline remains outside this scope.

## Identity approach accepted

ADR-009 accepts External ID/SPA PKCE, APIM plus independent API validation, Aquarium internal-user mapping/access authority, Tracking owner checks, worker managed identities and trusted actor context, and fail-closed behaviour. Registration methods, exact claims/scopes/app roles/issuers, tenant/app setup, local identity and delegation protocol remain open. No identity infrastructure has been configured.

## Hosting, ingress and configuration decisions accepted

HOST-01/NET-01–02/CONFIG-01–02 record accepted ADR-011/026/027. Stage 1 still needs plan compatibility/headroom, sufficiently narrow reliable addressing/operational access, config/secret RBAC, local developer access, refresh/rotation/failure policies. No Front Door/WAF initial dev deployment and no broad Azure-region allowlist fallback. These decisions do not close actual configuration/verification tasks.

## Service-level configuration isolation accepted

CONFIG-03/04 and ADR-027 accept per-service least privilege, explicit nonsecret sharing and separate runtime/deployment permissions. Verify shared-store enforcement; propose separate instances if necessary without silently broadening access. Exact roles/scopes/developer grants and operational implementation settings remain open; refresh/rotation approaches are now accepted; no real grants were configured.

## Consolidated Stage 1 decisions accepted

CONFIG-05–07/ADR-027 close the operational refresh/rotation/failure approach; exact timing/provider settings remain open. DEV-01–02/ADR-029 accept individual developer identity and hybrid Local strategy; roles/tools remain to configure. ENG-01/ADR-002 accepts internal layering. TECH-01–03/ADR-028 accept backend/frontend majors, direct Cosmos SDK and version policy.

This supersedes earlier current-policy TBD wording in this register: no reapproval of accepted approaches is needed. Remaining work includes exact version/compatibility matrix, actual access grants, local setup, runtime/rotation/retry details, quality/agent controls, observability and operating targets. Stage 1 completion evidence is still pending.

## Testing decisions accepted and remaining Stage 1 work

TEST-01/02 and [ADR-030](../architecture/decisions/adr-030.md) accept the testing layers, applicable passing PR gates, xUnit and Playwright Test/TypeScript with Chromium PR/broader pre-release browser coverage. Vitest/TestBed stays selected. No blanket coverage percentage initially; backend assertion tooling and concrete CI/test setup remain open.

The [Stage 1 readiness guide](stage-1-readiness.md#current-completion-path) is the current consolidated readiness list. It distinguishes unresolved configuration/operational choices from proof that accepted designs are implemented. Later-stage feature decisions are not blanket Stage 1 blockers.

## Customer sign-in refinement — 21 October 2026

ID-06–08/[ADR-009](../architecture/decisions/adr-009.md) accept dedicated customer tenancy, tenant-specific authority/local email-passcode flow, delayed social/federated sign-on and same-email Microsoft/customer isolation safeguards. [Approval evidence](authorised-decisions-2026-10-21.md). Initial registration-method choice is closed; tenant/apps/scopes/roles, session/MFA, workload delegation and verification remain pending.

## Customer MFA sequencing accepted

ID-09/[ADR-009](../architecture/decisions/adr-009.md): mandatory customer MFA deferred through Stages 1–5; Stage 6 requirements/launch review must decide MFA/recovery/billing-change protections. Revisit earlier for material risk changes. Administrative security remains separate. This closes Stage 1 customer MFA sequencing, not session configuration or the eventual commercial policy.

## Customer session handling accepted

ID-10/[ADR-009](../architecture/decisions/adr-009.md) accepts MSAL Angular/localStorage, silent token acquisition with interactive fallback, sign-out/cache cleanup and account-safe in-memory draft handling. Exact library versions, cross-tab verification and tenant session-duration/persistence settings remain pending; storage choice is closed.

## Customer permission split accepted

ID-11/[ADR-009](../architecture/decisions/adr-009.md) accepts separate Aquarium/Tracking delegated read/write permissions and independent tank ownership checks. Exact scope names/URIs, audiences, registration/consent and route mappings remain pending; Advisor permissions are deferred to Stage 5. Workload delegation is a separate decision.

## Synchronous delegation refinement

ID-12/[ADR-009](../architecture/decisions/adr-009.md) accepts OAuth OBO for synchronous customer-authorised API chains. Exact registrations, downstream permissions, caller restrictions and confidential-client authentication remain to verify. Worker delegation/context is separate.

## Durable worker context accepted

ID-13/[ADR-009](../architecture/decisions/adr-009.md) closes worker context authority: server-owned jobs plus workload authentication/current-access checks. Sender permissions, internal authorisation contracts, job statuses/retry settings and long-running recheck boundaries remain to specify. Provenance alone is not current access; committed fact publication is distinct.

## Internal workload boundary accepted

ID-14/[ADR-009](../architecture/decisions/adr-009.md) accepts dedicated worker operations and narrowly scoped permissions, Aquarium current-access/entitlement checks and later authorised Tracking history for Advisor. Exact callers/audiences/permissions/schemas and effective grants remain pending. API-025 retains OBO.

## Observability baseline accepted

OBS-01/[ADR-017](../architecture/decisions/adr-017.md) accepts Local/dev OpenTelemetry, safe structured logs/correlation and core operational metrics with shared Development monitoring and explicit Local Azure export. Retention, sampling, thresholds and responders remain to decide; instrumentation and effective access remain to verify.

## Development diagnostic policy accepted

OBS-02/[ADR-017](../architecture/decisions/adr-017.md) closes initial Development diagnostic retention/sampling/log-level policy. Actual table support/settings, SDK configuration and cost evidence remain pending. Alert thresholds/routing/responders and audit retention remain separate decisions; no shared-platform configuration changed.

## Development alert ownership accepted

OBS-03/[ADR-017](../architecture/decisions/adr-017.md) settles owner-operated Development monitoring, email notification and best-effort development-hours response. Destination address, actual routing/grouping/recovery settings and thresholds remain pending. Public support/escalation is a pre-Stage-4-launch gate.

## Development alert thresholds — accepted 21 October 2026

OBS-04/[ADR-017](../architecture/decisions/adr-017.md) accepts initial Development API/outbox/DLQ/command-age/worker-failure triggers and review after observed traffic. Exact query/evaluation/recovery settings, effective telemetry access and routing verification remain pending. Latency/resource alerts await targets and measured capacity.

## API latency target accepted

PERF-01/NFR-002 accepts 750 ms p95, separate read/write measurement through APIM including normal dependencies/commit, with stated exclusions and separate cold-start/failure reporting. [NFR specification](../requirements/non-functional-requirements.md). Load profile, harness and actual capacity evidence remain pending; no production availability target is accepted by this decision.

## Stage 2 identity configuration — accepted 21 October 2026

ID-15/[ADR-009](../architecture/decisions/adr-009.md) closes the first-slice registration/scope/user-key/OBO credential package. Three customer-tenant registrations, separate audiences, confirmed scope names, tid + oid mapping and certificate-authenticated Tracking OBO are accepted. Actual GUIDs/URIs/redirects/certificate permissions and functioning exchange remain verification tasks.

## Stage 1 scope reduction

The [narrowed Stage 1 gate](stage-1-readiness.md#current-completion-path) supersedes broad readiness lists for progression to Stage 2. Large-load benchmarking is deferred by owner; latency target remains guidance to validate. Remaining choices are first-slice contracts and minimum reproducible tooling; accepted identity setup needs evidence rather than reapproval.

## Accepted profile preference and minimum tank contract — 21 October 2026

PROFILE-01/TANK-01 close minimum tank fields and registration-level explicit measurement preference. [Contract](../api/tank-and-profile-contract.md). Exact executable schema, quantity representation/precision and initial parameter catalogue/rules remain contract-readiness tasks. No new architectural boundary/store is introduced.

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

## Current Stage 1 decision closure — READY-01

[READY-01](authorised-decisions-2026-10-21.md) accepts preparing one reviewable Stage 2 readiness specification rather than continuing routine detail-by-detail Q&A. No further high-level decision is currently identified as a prerequisite to that preparation or read-only readiness evidence. Exact dependency versions, schemas/precision/seed variants and setup values remain specification outputs requiring compatibility validation and appropriate review, not fabricated approvals.

Scientific seed content and the final baseline need human review. Escalate only actual compatibility/feasibility conflicts or changes to accepted architecture/behaviour. Actual platform access/handover, reproducible setup/checks and Stage 1 completion evidence remain outstanding. See the [current completion path](stage-1-readiness.md#current-completion-path). Application implementation, shared-platform deployment/spend and merge remain separately authorised.

## Measurement history policies accepted — 26 October 2026

HISTORY-01–03 accept measurement-only versioning without full event sourcing, structured immutable audit entries, atomic replacement, optimistic concurrency and retry deduplication, logical deletion/restoration, active-only current views, preserved advice inputs and initial retention without automatic expiry. [ADR-006](../architecture/decisions/adr-006.md) records full behaviour; [approval evidence](authorised-decisions-2026-10-26.md). Physical panel/version representation, executable contracts and feasibility checks remain readiness work. Review retention before production; decide erasure permissions, actor-identity retention and dependent advice-snapshot handling before implementing permanent erasure. Other Tracking record lifecycles are separately scoped.
