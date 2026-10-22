# Authorised decisions — 21 October 2026

Status: Selective human approval; remaining pack retains its recorded status.

## Customer sign-in and account-isolation safeguards

Evidence: following the email-passcode proposal and same-email Microsoft-account discussion, the owner stated: “I agree with using Entra External ID and delaying social sign-on for a later stage. document this decision and the safeguards you have listed above.”

| ID | Accepted choice | Record |
| --- | --- | --- |
| ID-06 | Dedicated External ID customer tenant, tenant-specific ciamlogin.com authority and initial local email-passcode customer flow; social/federated sign-on deferred to a later, separately approved stage | ADR-009 |
| ID-07 | Do not use workforce B2B guest invitation redemption for customer registration; independently validate expected issuer/audience/signature/lifetime/permissions at APIM and APIs; stable identity mapping, no email-only linking or ownership | ADR-009; security |
| ID-08 | Show active customer account and provide sign-out/switch-account; test concurrent Microsoft/customer sessions with identical email addresses, wrong-issuer rejection and account isolation | ADR-009; testing strategy |

The acceptance records configuration intent, not a claim that cookies alone guarantee isolation or that each application visit requires a fresh passcode. Existing customer sessions may support normal SSO. Email passcode alone is not MFA. Exact tenant/app settings, session/renewal policy and future secure linking remain open; customer MFA sequencing is subsequently accepted below.

No tenant, registration, authentication configuration, account, application code or cloud resource was changed.

## Customer MFA deferral

Evidence: owner proposed excluding MFA until Stage 6 reassessment; after clarification of the data/account risks and separate administrative protection, requested “Update docs and proceed to next decision.”

| ID | Accepted choice | Records |
| --- | --- | --- |
| ID-09 | No mandatory customer MFA through Stages 1–5; reassess MFA, recovery and billing-change protection during Stage 6 detailed requirements before subscriptions/payments launch; revisit earlier on material risk change; administrator protections remain separate | ADR-009; security; delivery plan |

This records deferral rather than approval of a final Stage 6 MFA policy. No authentication settings were changed.

## Customer session handling

Evidence: owner accepted the session-handling proposal with localStorage replacing sessionStorage and requested documentation update and the next decision.

| ID | Accepted choice | Records |
| --- | --- | --- |
| ID-10 | MSAL Angular/localStorage token cache; silent acquisition/renewal with interactive fallback; application-cache cleanup and External ID sign-out; in-memory input retention during same-user reauthentication, clearing on account change/sign-out | ADR-009; security; testing strategy |

Cache persistence is separate from identity-provider session lifetime and does not guarantee indefinite sign-in. Cross-tab logout/account-change handling and supported MSAL compatibility need verification. Exact session durations/policies remain unselected. No code/tenant changes performed.

## Customer delegated API permissions

Evidence: owner agreed separate service read/write permissions combined with existing per-tank ownership checks, then requested documentation update and the next decision.

| ID | Accepted choice | Records |
| --- | --- | --- |
| ID-11 | Separate customer delegated read/write permissions for Aquarium and Tracking; API permission plus per-tank ownership both required; workload permissions separate; Advisor permissions later | ADR-009; security |

Aquarium.Read/Aquarium.Write and Tracking.Read/Tracking.Write remain proposed exact names, not deployed scope identifiers. No app registrations, consent or permissions changed.

## Synchronous service delegation

Evidence: owner agreed the OBO proposal for synchronous customer-authorised service calls, subject to exact External ID configuration verification, then requested documentation update and the next decision.

| ID | Accepted choice | Records |
| --- | --- | --- |
| ID-12 | OAuth OBO for synchronous customer request chains; Tracking validates its token and obtains Aquarium-specific delegated token; Aquarium validates delegation/permissions/ownership; worker managed-identity context remains separate | ADR-009; Aquarium validation contract |

Exact registrations/scopes/client authentication remain pending. No customer bearer tokens in persistent messages; no insecure fallback. No identity resources or application code changed.

## Durable worker context

Evidence: owner agreed server-owned job context, managed-identity workers and current-access checks for protected jobs, then requested documentation update and the next decision.

| ID | Accepted choice | Records |
| --- | --- | --- |
| ID-13 | API-authorised durable job/user/tank/operation/input context; outbox command references authoritative job; owning worker uses managed identity, validates consistency and checks current access/entitlements through Aquarium; temporary dependency failure retries, revoked access stops protected work | ADR-009; async processing |

Already-committed fact publication does not need renewed customer authorisation. Message fields alone confer no access; no persistent bearer tokens. Exact worker permission/contracts and execution recheck settings remain pending. No implementation or grants performed.

## Internal workload API permissions

Evidence: owner agreed dedicated internal operations and narrowly scoped workload permissions separate from customer delegated routes, then requested documentation update and the next decision.

ID-14 accepts approved worker identity plus operation permission and actor/tank/action checks; Aquarium current-access/entitlement operation; Tracking Advisor-history operation at Stage 5. Exact routes/schemas/callers/audiences/grants remain pending. API-025 retains synchronous OBO despite its internal URL. No code or permission changes.

## Local/Development observability

Evidence: owner agreed the proposed Local/dev observability baseline, then requested documentation update and next decision.

OBS-01 accepts OpenTelemetry APIs/workers, shared Development Application Insights/Log Analytics, HTTP/outbox/message correlation, structured safe logs and API/dependency/outbox/queue/DLQ/worker metrics. Local console by default; explicit Azure export. No credentials/private content/full payload logging; business/security audits separate from sampled diagnostics. ADR-017 remains Partially Accepted: retention/sampling/alerts/ownership still open. No platform changes, telemetry implementation or resource configuration performed.

## Development diagnostic retention and sampling

Evidence: owner agreed the initial Development retention/sampling proposal and requested documentation update and next decision.

OBS-02: target 30-day diagnostic retention subject to supported table settings/platform approval; 100% distributed traces initially at low dev traffic; Information-and-above logs with routine health-check noise suppression; temporary Debug/Trace investigation only; review volume/sampling before substantial load tests and coordinate sampling as volume grows. Audit retention is separate. No resource/settings changes or actual retention/cost verification performed.

## Development alert ownership

Evidence: owner agreed owner-operated Development monitoring, email notifications and best-effort response during development hours, then requested documentation update and next decision.

OBS-03 accepts project owner as initial operational owner, owner-designated email (not yet supplied/configured), safe diagnostic/recovery links, grouped repeats and recovery notifications, no overnight/24-hour obligation, and public support/escalation review before Stage 4 launch. Exact thresholds/configuration remain pending. No notification sending or platform configuration performed.

## Development alert thresholds — accepted 21 October 2026

Evidence: owner agreed the six proposed initial Development alert thresholds and their exclusions/dashboard/review behaviour, then requested documentation update and next decision.

OBS-04: initial Development investigation triggers, applied only as workloads become operational:

| Signal | Accepted Development trigger |
| --- | --- |
| API failures | HTTP 5xx rate >5% over 10 minutes with at least 20 requests |
| Low-traffic safeguard | At least 5 HTTP 5xx responses within 10 minutes, regardless of percentage |
| Unpublished outbox | Oldest pending record >5 minutes |
| Dead-letter messages | Any increase in DLQ count |
| Waiting commands | Oldest waiting command >10 minutes |
| Worker failures | At least 3 failed processing attempts within 10 minutes, including retries |

Exclude expected validation/access denials from unexpected API failure counts. Review thresholds after observing traffic. Successful processing drives applicable recovery notifications; DLQ alerts require investigation, not automatic replay. Latency, CPU/memory and dependency throttling are initially dashboard signals; alert settings follow agreed performance targets/measured shared-plan behaviour. These triggers are not availability guarantees. Exact evaluation cadence, signal scope/aggregation, recovery windows and implementation remain pending.

Records: ADR-017/observability/runbooks. No alert resources, shared-platform settings or notification delivery changed.

## Standard API performance target

Evidence: owner agreed 750 ms p95 for standard API operations with the proposed measurement boundary, then requested documentation update and next decision.

PERF-01 accepts NFR-002 p95 <=750 ms, reads and writes measured separately through APIM, including normal authorisation/validation/commit dependencies under agreed representative load. Interactive sign-in, binary uploads and async AI/image execution excluded; cold starts/dependency failures reported separately. This is a target, not verified capacity. Review implementation/capacity/cost before changing target or hosting. Load profile/harness remain pending. No load tests or infrastructure changes performed.

## Stage 2 identity configuration — accepted 21 October 2026

Evidence: owner agreed the Stage 2 identity configuration package and requested documentation update and next decision.

ID-15: approve three registrations in the dedicated customer tenant: Parameter Pilot UI, Aquarium API and Tracking API. Each API validates its own audience. Confirm delegated scope names Aquarium.Read, Aquarium.Write, Tracking.Read and Tracking.Write; full scope URIs/registration GUIDs remain actual setup outputs. Aquarium uniquely maps validated tenant ID plus object ID (tid + oid) to internal user ID; do not use email or application-specific sub for cross-API identity matching. Verify required claims and reject missing/untrusted identity context.

Only the approved Tracking application may use OBO for Aquarium panel validation, requiring Aquarium.Read and independent tank ownership. Route policies must also restrict the calling application; a scope alone does not approve all callers. Tracking authenticates as a confidential client using a registered certificate. Protect Development private key in Key Vault; local Tracking uses a separate local certificate outside source control. Select/verify secure supported library loading, private-key permissions, credential rotation and registration of both public certificates; no private key is shipped to the UI. Certificate authentication supplements, rather than replaces, the delegated OBO token.

Register explicit localhost redirect addresses for authorised Local development and explicit Development redirects; no invented/wildcard deployment addresses. Advisor registrations remain deferred. Exact GUIDs/audiences/URIs/redirects/certificate references and supported implementation are setup/verification tasks, not new product choices. No registrations, certificates, grants or settings were created.

## Accepted profile preference and minimum tank contract — 21 October 2026

PROFILE-01/TANK-01: owner agreed the minimum tank-creation contract and mandatory user-profile measurement preference with three explicit choices after discussion, and requested documentation update and next decision. Aquarium owns profile preference. Require explicit Metric/US customary/UK imperial selection at post-authentication registration completion, no default, before tank creation/measurement entry. Accepted tank fields/rules: trimmed required 1–100-character name (duplicates permitted), Freshwater/Marine, valid user-confirmed IANA timezone, optional positive estimated operating volume with explicit preferred unit, server GUID/internal owner/UTC creation time. Volume preference refines litres-only entry. Preserve stored quantities/units, convert/round only appropriately; parameter-specific unit rules remain. Snapshot current preference with future advice; historical text/context remains unchanged. [Contract](../api/tank-and-profile-contract.md). No implementation or schema migration performed.

## Initial parameter catalogue and selection — accepted 21 October 2026

Evidence: owner agreed the proposed initial catalogue and selection behaviour, then requested documentation update and next decision.

MEAS-05: Stage 2 offers pH, ammonia, nitrite, nitrate, phosphate, calcium, magnesium and alkalinity. Owner explicitly selects tank definitions; Freshwater/Marine does not silently restrict the catalogue. At least one selection is required before recording a panel. Each panel may contain any non-empty subset of selected parameters; testing every selected parameter is not mandatory. Custom definition creation remains Stage 3. Aquarium owns versioned allowed units/input rules; distinguish invalid input from unusual readings and do not reject merely outside a recommended aquarium range. Exact units/analyte basis and executable rule settings remain separate contract work. No catalogue seed or application behaviour implemented.

## Explicit measurement units and reporting basis — accepted 21 October 2026

Evidence: owner agreed explicit unit/basis definitions and deferred automatic cross-basis conversions, then requested documentation update and next decision.

MEAS-06: every seeded parameter definition explicitly specifies measured quantity, chemical reporting basis, allowed units, display label and validation rules (numeric format, permitted units and applicable bounds). No ambiguous generic ppm unit. Where reporting basis differs, use separate definition variants, especially for ammonia; the initial eight catalogue names are measurement families, not a restriction to exactly eight scientific definitions. Do not conflate total/free ammonia or elemental/compound reporting bases.

Preserve entered value and unit. Initially chart matching definitions/units together; defer automatic cross-basis conversions until reviewed. Scientific units remain independent of Metric/US customary/UK imperial profile preference. Exact seed variants, unit codes, numeric bounds/precision and executable schemas remain contract-readiness work; this approval does not assert those concrete scientific rules have been reviewed. No seed data, conversion engine or application code implemented.

## Measurement-panel contract — accepted 21 October 2026

Evidence: owner agreed the minimum panel contract and timestamp rule, then requested documentation update and next decision.

MEAS-07: measurement-panel submission identifies the tank in the route and checks ownership server-side. Require one offset-bearing measuredAt for the panel; backdating allowed; reject times more than five minutes ahead of server time. readings contains 1–50 entries, no duplicate parameterDefinitionId. Each entry requires definition GUID, positive definition revision, numeric value, explicit unitCode and qualifier (exact, belowDetectionLimit, aboveDetectionLimit). For detection-limit qualifiers the numeric value is the limit, not an exact measurement. Optional panel testMethod max 200 characters and notes max 4,000 characters.

Require an idempotency key: same authorised submission retry returns the original outcome without another panel. Conflicting payload follows the existing conflict policy. Server generates panel ID, recordedAt UTC and revision. Validate the complete panel through the accepted single Aquarium batch and local rules before atomic panel/idempotency/outbox persistence in the same Cosmos container/partition. No partial save. Profile completion, selected-definition eligibility and accepted explicit-unit/basis rules still apply. Exact executable schemas/error extensions and numeric precision/seed rules remain readiness work; no code or test execution performed.

## Submission errors and input preservation — accepted 21 October 2026

Evidence: owner agreed the proposed error-response and input-preservation contract, then requested documentation update and next decision.

MEAS-08: use consistent safe error bodies with stable code, explanation, trace ID and field details where applicable. Accepted mappings: 400 malformed request; 401 missing/expired authentication; 403 missing API permission; 404 absent/inaccessible tank without owner disclosure; 409 stale definition revision or idempotency-key payload conflict (distinct codes); 422 invalid readings/time; 503 temporary Aquarium/OBO unavailability. Only temporary OBO/dependency availability failures map to 503; actual authentication/permission failures retain their appropriate 401/403 semantics. Invalid or unusable trusted dependency responses fail closed without claiming a saved panel.

UI retains input for same-user reauthentication/retry, subject to ID-10 clearing on account change/sign-out. Refresh stale definitions while preserving entered values for review; never auto-resubmit after rules change. Field validation saves nothing. Permission/inaccessible-tank responses explain failure safely without exposing neighbour data. Do not expose tokens, internal exceptions or private dependency payloads. Rate-limit and unexpected-error conventions remain applicable; the table is not an exhaustive HTTP contract. No application changes or executable schema validation performed.

## Minimum Stage 2 Local setup — accepted 21 October 2026

Evidence: owner agreed the minimal Local setup and requested documentation update and next decision.

DEV-03: minimum Stage 2 Local setup runs Angular UI and Aquarium/Tracking APIs directly through development tooling. Docker Compose starts SQL Server Developer and Cosmos DB NoSQL emulator containers; use a small repeatable synthetic seed set. Actual Development External ID supports customer authentication/OBO. Select/pin supported compatible container/tool versions after verification; no preview assumption or floating latest pin. Local certificate and secrets follow ID-15/ADR-027.

Emulator/container results are not proof of Azure parity. Verify required operation support, including same-container/partition transactions, and real Development identity/permissions/cloud behaviour. If a required operation is unsupported locally, use the approved Development dependency for that check rather than building an inaccurate substitute. No unapproved resource creation/spend implied.

Advisor/PostgreSQL/photo dependencies wait for their stages. Add Service Bus and workers when the authorised implementation slice requires them; preserve core synchronous transaction/outbox design and do not fabricate broker-delivery evidence. Docker Compose manages dependencies, not a requirement to containerise local UI/APIs. No Compose file, dependencies, seeds, projects or resources created in this documentation update.

## Definition consistency — accepted 21 October 2026

Evidence: owner agreed validation-time definition consistency and requested documentation update and next decision.

MEAS-09: Aquarium validation is the definition-consistency point for a new panel. Aquarium validates submitted revisions and returns authoritative rules; Tracking applies those rules and persists exact definition IDs/revisions with the panel. A definition change after successful validation does not invalidate that accepted panel; the next new submission uses then-current definitions. Retain historical definition revisions so saved readings remain interpretable. A stale revision detected during validation returns the accepted 409 with input preservation.

No second Aquarium validation call or distributed SQL/Cosmos transaction is introduced. This consistency rule is limited to definition changes; it does not waive token validation or tank-ownership checks. Existing fail-closed dependency behaviour and same-container/partition local atomicity remain. Timing/retirement scenarios must be verified; no executable behaviour changed.

## Stage 2 readiness-specification approach

Evidence: owner agreed preparing a concrete readiness specification for review before application implementation, then requested “Update docs and explain any further decisions required before moving to other tasks required before Stage 1 is considered done.”

READY-01: prepare exact compatible SDK/package/container selections, executable tank/profile/panel API schemas, initial parameter seed definitions with explicit units/basis/rules, configuration placeholders, reproducible Local instructions and a compact platform/evidence checklist. Routine details follow accepted design rather than requiring individual Q&A approvals. Scientific seed definitions require explicit review; generated records are not automatically accepted. Escalate deviations affecting ownership, stores, security, contracts or required behaviour. Present the concrete baseline for human review before application implementation.

No additional high-level architecture/product decision is identified as a prerequisite to preparing this specification or gathering read-only readiness evidence. Exact versions/schemas/settings are preparation outputs. Compatibility failures or conflicts may require focused decisions later. This approval does not approve seed content in advance, application implementation, shared-platform changes/deployment/spend or merge. This turn records the approach only; the specification has not been produced.
