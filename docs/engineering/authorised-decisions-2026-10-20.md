# Authorised asynchronous-processing decisions — 20 October 2026

Version: 0.10 | Date: 20 October 2026 | Status: Accepted design decisions

## Approval evidence and scope

The human owner described the large-system demonstration goal, proposed service-owned workers and then accepted the assistant's recommendations with “Agree with your recommendations. Update the architecture pack to match.”

Acceptance includes the recommendations that qualify the original proposal: core writes remain synchronous, workers never write another service's store, messages use separate queues/subscriptions, and shared-plan hosting requires verification. It does not approve the original idea of queueing all CRUD or sharing one event database.

| ID | Accepted decision | Records |
| --- | --- | --- |
| ASYNC-01 | Three service-owned logical workers/Function Apps: Aquarium, Tracking, Advisor; remove generic Event Processor | ADR-012 |
| ASYNC-02 | Synchronous tank/measurement/maintenance/observation CRUD; commit local state and outbox atomically; workers publish asynchronously | ADR-007 |
| ASYNC-03 | Each worker accesses only its service's stores. Tracking Cosmos is product history, not a shared integration/telemetry/event-sourcing store | ADR-003 |
| ASYNC-04 | One Service Bus namespace; service-addressed command queues and topic subscriptions/filters per relevant consumer; competing consumers on one queue do not broadcast | ADR-008 |
| ASYNC-05 | Intended starting deployment: three Function Apps on the existing shared-platform App Service Plan, subject to OS/SKU/runtime/capacity and Always On verification | ADR-012; ADR-022 |
| ASYNC-06 | Each API/worker emits OpenTelemetry directly and propagates message trace context; no business queue solely for diagnostic tracing | ADR-017 (partial) |
| ASYNC-07 | Initial photo processing is functions within Tracking Async Worker, not a fourth independently owned processor | ADR-012; ADR-016 |
| ASYNC-08 | Expensive/deferred work includes advice, photo processing, approved projections/integrations; future asynchronous ingestion requires deliberate job/status/backpressure design | Dynamic flows; delivery plan |

## Boundaries and remaining choices

Shared hosting provides logical isolation/deployment ownership, not independent compute scaling. Verify identity/data permissions, max concurrency, CPU/memory/connection capacity, plan support and operational ownership. Extraction to separate compute requires an approved change based on contention/backlog/latency evidence.

Exact names, tiers, retry counts, message lock/lease settings, Cosmos index/settings details, payload schema details, alert thresholds and host runtime versions remain open where not separately approved. No dummy consumers or projections are required solely to demonstrate architecture.

No application implementation, provisioning, shared SKU change, spending or merge is authorised.

## Parameter-definition and measurement-panel acceptance

Approval evidence: the owner retained measurement-panel JSON documents and then accepted the described Tracking-to-Aquarium validation architecture with “I agree with the above proposed architecture. Update the pack accordingly.”

| ID | Accepted refinement | Records |
| --- | --- | --- |
| MEAS-01 | Aquarium owns GUID-identified SQL definition records, scientific revisions/rules/units and tank selection; UI fetches selected definitions for entry | ADR-023; US-009 |
| MEAS-02 | Tracking stores readings measured together as one panel; each reading references definition ID/revision with value/unit/qualifier | ADR-023; FR-003 |
| MEAS-03 | Tracking makes one direct batched call to Aquarium for authorised tank eligibility and all referenced definitions/rules; applies trusted validation before saving | ADR-023; API-025 |
| MEAS-04 | Reject stale revisions with refresh feedback; on Aquarium failure persist neither panel nor outbox, preserve UI input and permit retry | ADR-023; API-005 |

At MEAS acceptance optional per-reading definition display snapshots and /tankId were not approved; DATA-04 below subsequently accepts /tankId, while display snapshots remain Proposed; detailed rule thresholds, timeout/error schemas, cache/projection policy and commercial boundaries are not newly accepted. General implementation/deployment authority is not granted.

## Accepted shared-platform data placement and partitioning

Approval evidence: the owner accepted the platform/application ownership split, then Aquarium schema in ReferenceProjectsDb, then “I agree with /tankId as partition key. I agree with above recommendations regarding Cosmos container ownership and Aquarium DB schema. Update docs”.

| ID | Accepted choice | Records |
| --- | --- | --- |
| DATA-01 | Platform owns shared hosting/capacity, SQL server/database, Cosmos account/database/throughput, Service Bus namespace and platform-wide policies; app owns approved child resources, identities and scoped configuration | ADR-024; ADR-022 partial |
| DATA-02 | Aquarium schema inside platform-owned ReferenceProjectsDb; app tables/migrations/outbox/inbox and migration history schema-scoped; runtime identities access only this schema | ADR-024; ADR-004 partial |
| DATA-03 | Tracking-owned containers/indexes/lifecycle inside platform-owned ReferenceProjects Cosmos database; Tracking API/worker container-scoped access | ADR-024 |
| DATA-04 | /tankId partition for the proposed tank-scoped Tracking container; business state and its outbox in same container/logical partition for atomicity | ADR-005 |

These supersede earlier “partition proposed” wording in MEAS acceptance and other documents. Optional per-reading definition snapshots stay proposed. Exact names/indexes/roles/retention, deployed resource availability, capacity and effective permissions remain to be verified. No platform Bicep edits, resource creation, role assignment, migration or spending is authorised here.

## Accepted environment scope and external platform prerequisite

Evidence: the owner accepted shared APIM/ACR/Key Vault/App Configuration/Blob/PostgreSQL hosting and stated azure-reference-platform would be updated/deployed separately before agentic development; then explicitly agreed “Local and Development only, deferring Test and Production provisioning until release preparation. Update docs”.

| ID | Accepted choice | Records |
| --- | --- | --- |
| ENV-01 | Local and Development initially, using synthetic data and development identities | ADR-025; development/environments.md |
| ENV-02 | Test/Production provisioning deferred until release preparation; automated testing still starts immediately | ADR-025; delivery plan |
| PLATFORM-01 | Platform owns shared APIM/ACR/vault/config-store/storage-account/PostgreSQL-server hosting; app owns approved API/image/config/secret/container/database content | ADR-024 refinement |
| PLATFORM-02 | Platform changes/deployment are separately owner-requested work outside Parameter Pilot agentic process; verify pre-existing hosting before app implementation | ADR-024/025; platform inventory |

PostgreSQL server ownership moves to platform; Advisor database/data ownership stays with Advisor. Existing inspected source did not establish additions exist. Enforce isolation for shared vault/configuration; use separate instances if necessary. No platform changes/deployment, Test/Production provisioning or spend is authorised by this documentation task.

## Accepted CI/CD authority

Evidence: owner's explicit acceptance of GitHub Actions as sole Parameter Pilot CI/CD authority and migrating/retiring existing Azure DevOps pipelines, followed by “Update docs”.

| ID | Accepted choice | Record |
| --- | --- | --- |
| CI-01 | GitHub Actions is sole Parameter Pilot CI/CD authority for PR/build/security/image publishing and app deployment; use shared ACR, scoped Azure OIDC and human merge approval | ADR-018 |
| CI-02 | Verify replacements, coordinate noncompeting cutover, then retire legacy Azure DevOps definitions/YAML and obsolete app-specific access following dependency review | ADR-018 |
| CI-03 | Initial cloud target dev only; Test/Production wait for release preparation; platform pipeline remains separately managed | ADR-018/024/025 |

Acceptance does not assert workflows/branch rules/OIDC or retirement exist. No pipeline settings/files, credentials, platform configuration or resources are changed in this documentation task.

## Accepted identity and authorisation

Evidence: owner's “I agree. Update pack.” in response to the six-point identity proposal.

| ID | Accepted choice | Record |
| --- | --- | --- |
| ID-01 | External ID customer sign-in from Angular using authorisation code + PKCE; API access token through APIM | ADR-009 |
| ID-02 | APIM and every receiving API independently validate applicable tokens/permissions | ADR-009 |
| ID-03 | Aquarium maps validated identity to internal user and owns tank access; email/browser IDs never establish ownership | ADR-009 |
| ID-04 | Tracking checks through Aquarium including the accepted batch; workers use managed identities with trusted originating actor/tank context | ADR-009/023 |
| ID-05 | Required authorisation unavailable/invalid means fail closed | ADR-009 |

Specific registration methods, actual token/tenant/app/role configuration, delegation and local identity remain TBD. No tenant changes, app registrations, permissions or deployment are performed in this docs update.

## Accepted Development hosting, ingress and configuration

Evidence: owner accepted separate shared-plan API apps, APIM-only browser traffic/Front Door deferral, restricted public backends subject to addressing verification, and the configuration/secrets arrangement; then requested “Update docs on agreed above”.

| ID | Accepted choice | Records |
| --- | --- | --- |
| HOST-01 | Separate containerised API apps on shared Linux plan with workers; app identities/configuration separate; Advisor later; verify capacity | ADR-011 |
| NET-01 | Browser traffic via shared APIM HTTPS, independent API checks; no direct browser backend access; defer Front Door/WAF to release preparation | ADR-026 |
| NET-02 | Restricted public HTTPS backends; allow narrow verified APIM/necessary workload sources and deny others; no broad-region fallback; revisit if not feasible | ADR-026 |
| CONFIG-01 | Nonsecret config/flags in App Configuration; unavoidable secrets in Key Vault; deployed managed identities where supported | ADR-027 |
| CONFIG-02 | Local nonsecret defaults in source, local secrets untracked User Secrets/equivalent; no browser/source/log secrets; labels/prefixes not access boundaries | ADR-027 |

Exact plan tier/headroom, effective addresses/access rules, configuration permissions, refresh/rotation/failure policies and local developer access are not accepted settings yet. No actual platform, networking, identities, secrets or deployments are changed.

## Accepted service configuration/secret access boundaries

Evidence: owner's “Agreed. Update docs and list here which .md files contain the above information” after the per-service least-privilege and separate runtime/deployment proposal.

| ID | Accepted choice | Record |
| --- | --- | --- |
| CONFIG-03 | Aquarium/Tracking/Advisor API and worker identities read only their respective required settings/secrets; explicit sharing allowed for nonsecrets, not automatic cross-service secret access | ADR-027; service access matrix |
| CONFIG-04 | Deployment configuration-management permissions separate from runtime readers; verify enforceable shared-store isolation, propose separate stores/vaults if necessary rather than silently broadening access | ADR-027 |

Each workload retains its own identity and minimum grants. At that approval exact developer-access and operational policy choices were unresolved; DEV-01 and CONFIG-05–07 below subsequently accept those approaches. Exact grants/timers/provider settings remain TBD. No permissions/credentials/platform resources changed.

## Consolidated operational, engineering and technology acceptance

Evidence: after the service-isolation update the owner explicitly agreed each proposal below and requested “Agreed. Update docs with outstanding decisions above” after the frontend decision.

| ID | Accepted choice | Records |
| --- | --- | --- |
| CONFIG-05 | Startup loading/controlled restart for initial dev changes; dynamic flag refresh deferred; jobs keep starting config | ADR-027 |
| CONFIG-06 | Operator-controlled secret rotation; provider-supported overlap, replacement/Key Vault update/restart/verify then revoke; maintenance if no overlap; prompt incident response | ADR-027 |
| CONFIG-07 | Required config missing/invalid/unavailable at startup means not Ready; safe diagnostics/bounded retry; loaded runtime config usable only while authorisation/dependencies valid; no insecure fallback/false success | ADR-027 |
| DEV-01 | Individual Entra developer identities/scoped dev access via approved login; no shared accounts/copied workload credentials, separate administration | ADR-029 |
| DEV-02 | Hybrid Local dependencies/doubles with dev Azure for unsupported features and real-Azure integration checks | ADR-029 |
| ENG-01 | Proportionate Clean Architecture with service-local API/worker Application/Domain reuse and technical-only cross-service sharing | ADR-002 |
| TECH-01 | .NET 10/ASP.NET Core 10/C# 14, relational EF Core 10/compatible providers, isolated Functions subject to compatibility; pin exact versions/reviewed patches/no previews | ADR-028 |
| TECH-02 | Direct Cosmos .NET SDK in Tracking Infrastructure through narrow interfaces; relational EF unchanged | ADR-028; ADR-004 partial |
| TECH-03 | Angular 22, strict TS/templates, feature-oriented standalone components, client SPA/no initial SSR, Vitest/TestBed, compatible pinned Node/tooling and lockfile | ADR-028 |

Exact versions/provider support, role assignments, emulator tools/images, retry/timing values, secret lifetimes and concrete restart/draining/renewal configuration remain TBD. No dependencies installed, apps restarted, credentials rotated, identities granted or cloud resources deployed.

## Accepted testing and browser verification

Evidence: owner agreed the automated testing strategy, agreed the Playwright proposal, then requested “Agreed. Update docs with decisions and list here outstanding decisions before Stage 1 considered done.”

| ID | Accepted choice | Records |
| --- | --- | --- |
| TEST-01 | Risk-based unit/component/integration/contract/security/critical E2E tests; backend xUnit; applicable build/static/tests pass before merge; failures block merge; no blanket coverage percentage initially; later AI evaluations | ADR-030; testing strategy |
| TEST-02 | Playwright Test with TypeScript; small Chromium PR suite, broader Firefox/WebKit checks before release; synthetic data/controlled accounts; generated auth state excluded from source; protected reports | ADR-030; testing strategy |

Vitest/TestBed remains accepted for frontend unit/component tests. Exact versions, backend assertion library, workflow enforcement and test/report configuration remain pending. No test execution, dependency installation, pipeline configuration or deployment is claimed.
