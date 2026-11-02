# Stage 2 readiness specification

Date: 29 October 2026 | Status: Accepted baseline; implementation and environment evidence pending

Authority: READY-01 in the [21 October record](authorised-decisions-2026-10-21.md). This prepares item 1 of the [Stage 1 completion path](stage-1-readiness.md#current-completion-path). Human acceptance of SPEC-01–04 is recorded in the [29 October decision record](authorised-decisions-2026-10-29.md). Acceptance does not implement the application, establish cloud access, or complete Stage 1. Existing accepted behaviour remains authoritative. The Structurizr workspace and included model remain unchanged.

## Accepted decisions — 29 October 2026

| ID | Accepted recommendation | Scope/status |
| --- | --- | --- |
| SPEC-01 | Adopt the exact candidate dependency versions and image digests below; use built-in xUnit assertions without another assertion library. | Published metadata checked; restore/build and real hosting verification pending. |
| SPEC-02 | Use the candidate wire names, routes, schemas and limits below. Preserve entered measurement numbers/units with decimal processing; never silently round input. | Concrete routes, wire names, limits and representation choices accepted; runtime verification pending. |
| SPEC-03 | Start with the 12 explicit scientific definition variants below, covering the eight accepted families. Initially use mg/L with explicit reporting basis; no generic ppm, automatic cross-basis conversion or dKH conversion. | The 12 definitions, units, qualifiers and bounds are accepted as the initial scientific baseline; later kit-specific additions require review. |
| SPEC-04 | Use the proposed Local ports/configuration and startup sequence below. Prefer the non-vnext Linux Cosmos emulator pinned by digest; prove its operations before using it as evidence. | No Compose file, application project, secret or resource created. Unsupported behaviour uses an already authorised Development dependency; otherwise stop for a focused decision. |

The owner accepted the presented recommendations with “I accept the above recommendations.” This accepts SPEC-01–04, including the concrete contracts and 12 scientific seed variants. References below to candidates/proposals describe the reviewed artefacts; they no longer mean acceptance is outstanding. Publication, installation and practical correctness checks remain separate. No new service, store, tenant, provider or public exposure is proposed.

## Exact candidate dependencies

Publisher metadata was read on 29 October 2026. These are candidate direct dependency pins, not installed tooling or a resolved application lockfile. Do not choose independent latest versions during implementation. Record transitive dependencies, licence notices, vulnerabilities and restore results when authorised projects exist.

| Area | Candidate pin | Evidence/constraint |
| --- | --- | --- |
| .NET SDK / C# | SDK 10.0.403 / C# 14 / net10.0 | [.NET 10 download](https://dotnet.microsoft.com/en-us/download/dotnet/10.0); propose disabled SDK roll-forward for reproducibility. |
| ASP.NET runtime | 10.0.14 | Same publisher release page; candidate Linux Ubuntu Noble image below. |
| EF Core | Microsoft.EntityFrameworkCore.SqlServer and Microsoft.EntityFrameworkCore.Design 10.0.14; dotnet-ef 10.0.14 | [SQL provider](https://www.nuget.org/packages/Microsoft.EntityFrameworkCore.SqlServer/10.0.14); align EF tools/packages. No PostgreSQL dependency in this slice. |
| Tracking store | Microsoft.Azure.Cosmos 3.63.3 | [Publisher package](https://www.nuget.org/packages/Microsoft.Azure.Cosmos/3.63.3); Infrastructure only, no EF Cosmos provider. |
| API identity | Microsoft.Identity.Web 4.16.1 | [Publisher package](https://www.nuget.org/packages/Microsoft.Identity.Web/4.16.1); certificate OBO and External ID issuer/audience still require verification. |
| Azure credentials | Azure.Identity 1.21.0 | [Publisher package](https://www.nuget.org/packages/Azure.Identity/1.21.0); Local developer login distinct from workload/customer identity. |
| App Configuration | Microsoft.Extensions.Configuration.AzureAppConfiguration 8.6.1 | [Publisher package](https://www.nuget.org/packages/Microsoft.Extensions.Configuration.AzureAppConfiguration/8.6.1); include only when its adapter is implemented. |
| Development telemetry | Azure.Monitor.OpenTelemetry.AspNetCore 1.6.0 | [Publisher package](https://www.nuget.org/packages/Azure.Monitor.OpenTelemetry.AspNetCore/1.6.0); local console remains the default. |
| Backend tests | xunit.v3 4.0.2; Microsoft.NET.Test.Sdk 18.11.0; xunit.runner.visualstudio 4.0.1 | [xUnit releases](https://xunit.net/releases/); use built-in Assert, verify runner discovery on net10.0. |
| Node/npm | Node 24.22.2 LTS; bundled npm 11.19.1 | [Node release index](https://nodejs.org/dist/index.json), release dated 27 October; do not replace npm with its independent latest. |
| Angular framework | @angular/* framework packages 22.2.3, including compiler/compiler-cli | [Core metadata](https://registry.npmjs.org/@angular/core/22.2.3); keep framework/compiler patches aligned. |
| Angular tooling | @angular/cli and @angular/build 22.2.5 | [Build metadata](https://registry.npmjs.org/@angular/build/22.2.5); compatible framework ^22.0.0, TypeScript >=6.0 <6.1 and Vitest ^4.0.8 or ^5.0.0. |
| TypeScript / RxJS / tslib | 6.0.3 / 7.8.2 / 2.8.1 | [Angular compatibility](https://angular.dev/reference/versions); TypeScript 7.0.2 is published but outside the compiler's supported range. |
| UI tests | Vitest 5.0.5, jsdom 30.1.3, Angular TestBed from 22.2.3 | [Vitest metadata](https://registry.npmjs.org/vitest/5.0.5), [jsdom metadata](https://registry.npmjs.org/jsdom/30.1.3); both support selected Node. Run component tests before calling this compatible in practice. |
| Browser tests | @playwright/test 1.64.1 | [Publisher metadata](https://registry.npmjs.org/@playwright/test/1.64.1); use the matching managed browser revisions, Chromium initially. |
| Contract verification only | Python 3.14; jsonschema[format] 4.25.1 | Used for this specification's structural checks; not an application runtime requirement. |

Metadata selection does not establish the complete auth/browser/telemetry dependency graph. Select and lock any additional direct adapters at their implementation slice, and verify licence/security/peer constraints. Do not add Advisor, photo, charting or worker packages prematurely. Functions 4.x supports isolated .NET 10 according to [Microsoft's guide](https://learn.microsoft.com/en-us/azure/azure-functions/dotnet-isolated-process-guide); exact worker/extensions and actual shared-plan support remain required before the worker slice, not a requirement to deploy a worker now.

### Immutable image candidates

MCR returned these digests for the named tags on 29 October. Use `mcr.microsoft.com/<repository>@sha256:<digest>` in future authorised manifests; tags below identify the inspected release and must not become floating runtime pins. Image availability is verified; image signatures, OS/CPU compatibility, execution and scans are not.

| Repository | Inspected tag | Digest |
| --- | --- | --- |
| dotnet/sdk | 10.0.403-noble | sha256:de4fe90a98845d75910b9769662465c84de1a934665c431279d1382b2bddc02b |
| dotnet/aspnet | 10.0.14-noble | sha256:de0ee358cdd672f7017a003bed21e9ac9ed48a27c922a59b18175b6e82fa7fee |
| mssql/server | 2022-CU27-ubuntu-22.04 | sha256:4402d880dd4c34bfa7d8705e56a86cd6c88da80a1f6bbbe741f999e76264a090 |
| cosmosdb/linux/azure-cosmos-emulator | latest (resolved once; non-vnext image) | sha256:ff955bdc5b191228425ee7072f99b151c7f7406ae7ed0be1b3ba8cbaa287a7e9 |

Use SQL Server Developer for Local nonproduction use. SQL Server on Linux and the selected Cosmos image require a compatible x64 container host; do not assume ARM support or cross-architecture emulation support. The [Cosmos emulator documentation](https://learn.microsoft.com/en-us/azure/cosmos-db/linux-emulator) identifies differences from Azure. Do not silently substitute vnext-preview or bypass TLS validation. Verify SDK connectivity, provisioning, queries and same-container/same-/tankId transactional batches; broker/cloud identity/security cannot be proved by the emulator.

## Candidate executable contracts

The [JSON Schema bundle](../api/schemas/stage-2.schema.json) uses Draft 2020-12, closed request objects and separate response shapes. It is executable data validation, not a complete OpenAPI document or implemented HTTP service. Select a named `$defs` schema. SPEC-02 now supplies accepted concrete details alongside the existing [profile/tank](../api/tank-and-profile-contract.md), [batch validation](../api/aquarium-validation-contract.md) and [panel](../api/tracking-openapi-draft.md) behaviour; raise actual conflicts rather than silently changing either.

| Operation | Candidate route / schema | Authorisation and result |
| --- | --- | --- |
| Read/complete/update profile | GET/PUT /api/v1/me/profile; Profile / ProfileUpdate | Aquarium delegated user; self only. GET can return completed:false without a measurement choice; PUT requires explicit choice, returns completed profile. Exact new route/PUT semantics proposed. |
| Create tank (API-001) | POST /api/v1/tanks; TankCreate -> Tank | Aquarium delegated write, completed profile; 201, Location and ETag. Require Idempotency-Key on creation. |
| Read tank (API-003) | GET /api/v1/tanks/{tankId}; Tank | Aquarium delegated read and current owner; inaccessible/absent -> 404. |
| Select built-in definitions | PUT /api/v1/tanks/{tankId}/parameter-definitions/selection; SelectionUpdate -> DefinitionList | Proposed route distinct from later custom-definition creation. Aquarium owner/write, completed profile, If-Match; replace selection, 200 and new ETag, stale ETag -> 412. Empty selection permitted but cannot record panels; max 50 selected definitions proposed. |
| Discover selected definitions (API-004) | GET /api/v1/tanks/{tankId}/parameter-definitions; DefinitionList | Aquarium owner/read; response contains current rules, not private store records. |
| Record panel (API-005) | POST /api/v1/tanks/{tankId}/measurement-panels; PanelCreate -> Panel | Tracking delegated write; required Idempotency-Key; trusted Aquarium check then Cosmos transaction; 201, Location and ETag. Authorised identical replay returns original response without another panel. |
| Retrieve committed panel | GET /api/v1/tanks/{tankId}/measurement-panels/{panelId}; Panel | Proposed exact retrieval route for first-slice verification; Tracking read plus trusted current Aquarium ownership. API-006 history/pagination is a separate contract, not supplied here. |
| Aquarium batch (API-025) | POST /internal/v1/tanks/{tankId}/measurement-validation-context; ValidationRequest -> ValidationContext | Existing proposed route; Aquarium-audience OBO token with Aquarium.Read, approved Tracking caller and current owner/profile/selection. Success 200; one exact authoritative result per requested pair, never partial eligibility. |
| Failures | Problem | Safe RFC 9457 body; stable code/traceId, optional errors using JSON-pointer paths. No raw exceptions, token or dependency payload. |

Schema for the tankId/panelId route values is UUID. Header Idempotency-Key uses its named schema: 16–128 characters, exact opaque value scoped by actor/operation/tank as applicable. Candidate initial retention is seven days (existing convention is proposed); agree before implementing expiry. Hash equivalent parsed payloads after documented normalisation, not JSON property order; preserve reading array order initially and document it in the client contract. Do not replay before authenticating and checking current authority. Invalid identifiers/JSON/shape -> 400; semantic rules -> 422. Use 401/403/404/409/412/413/422/429/503 as applicable, without revealing cross-owner existence. Missing API scope -> 403; actual authentication failure -> 401, not 503.

### New limits and representation choices for review

- Profile wire values: `metric`, `usCustomary`, `ukImperial`; water type: `freshwater`, `marine`; explicit volume units: `L`, `gal-US`, `gal-UK`. No preference defaults. Preserve the entered volume value/unit as authoritative; conversion for presentation must not rewrite it. Candidate conversion factors are 1 US liquid gallon = 3.785411784 L and 1 UK imperial gallon = 4.54609 L, with two decimal places and midpoint-to-even rounding for volume display only. The US factor follows 231 cubic inches and the exact 0.0254 m inch; see [NIST unit definitions](https://www.nist.gov/document/nist-hb-44-2024-appendix-c-general-tables-units-measurement) and [NIST conversion tables](https://www.nist.gov/pml/special-publication-811/nist-guide-si-appendix-b-conversion-factors/nist-guide-si-appendix-b8). Conversion/repeated-preference-change tests remain required before implementation acceptance; rounded display values never replace source quantities.
- Proposed technical decimal envelope: measurement numbers from -1,000,000 to +1,000,000 inclusive, at most six decimal places; positive volume up to 1,000,000 in its explicit unit, at most six places. This is an input/storage envelope, not an aquarium safety range. Parse as decimal on the server; reject excess precision/range, do not round silently or store raw binary floating-point approximations. Stage 2 UI must preserve the entered decimal text until validated submission. Per-definition scientific constraints can narrow the envelope only after review.
- Tank name is trimmed before length checks. Timezone must exist in the supported IANA database; a syntactically valid string is insufficient. Returned server timestamps are UTC `Z`; panel input requires an explicit offset and permits backdating, with the accepted five-minute future bound.
- Proposed maximum uncompressed UTF-8 JSON body: 64 KiB for profile/tank/selection/panel and internal validation requests; reject oversized bodies with 413 even with missing/misleading Content-Length. Candidate requests do not support compressed bodies; reject unsupported Content-Encoding with 415. Internal validation responses limited to 256 KiB; excess/unusable responses fail closed as 503. Gateway/backend limits must agree. These are new limits for review, not already implemented controls.
- Preserve accepted 1–50 readings, method 200 characters, notes 4,000 characters, positive definition revision, no duplicate definition IDs and no partial save. Define string lengths as Unicode code points; malformed Unicode is rejected. No arbitrary small scientific maxima or pH 0–14 clamp is inferred.
- Proposed profile-incomplete error: 422 / `profile-incomplete`. Accepted stale definition -> 409 / `parameter-definition-revision-stale`; key conflict -> 409 / `idempotency-key-payload-conflict`; temporary trusted validation failure -> 503 / `measurement-validation-unavailable`. Error paths must not echo submitted private values.

JSON Schema cannot enforce identity/ownership, IANA membership, time relative to the server clock, unique IDs across reading objects, exact trusted-response coverage, per-definition eligibility/unit rules, payload bytes, decimal parser behaviour or transactional persistence. Implement and meaningfully verify these at the owning runtime boundary. The structural test deliberately accepts repeated reading objects; that is not permission for runtime duplicates. Validate success-response tank ID, count, requested identities/revisions, supported units/rules, completed profile and trusted origin; invalid context means no write. Successful validation establishes definition consistency at that time; no second check or distributed transaction is added.

## Scientific seed proposal

The [machine-readable seed proposal](../api/schemas/stage-2-seed-proposal.json) contains 12 stable candidate GUIDs at revision 1. They are accepted as the initial catalogue baseline; installation remains part of separately authorised implementation. All eight accepted families remain available to either water type; no automatic selection. Distinct bases retain distinct IDs even when a unit code is shared.

| Family | Proposed definition / allowed unit |
| --- | --- |
| pH | Reported hydrogen-ion activity index; pH; exact qualifier only. Test-method scale must be identifiable; no conversion between scales is claimed. |
| Ammonia | Total ammonia nitrogen (NH3 + NH4+, as N), mg/L-as-N; separate free un-ionised ammonia as NH3, mg/L-as-NH3. No automatic TAN/free conversion. |
| Nitrite | Separate definitions expressed as NO2 (mg/L-as-NO2) and as N (mg/L-as-N). |
| Nitrate | Separate definitions expressed as NO3 (mg/L-as-NO3) and as N (mg/L-as-N). |
| Phosphate | Separate orthophosphate definitions expressed as PO4 (mg/L-as-PO4) and as P (mg/L-as-P); neither means total phosphorus. |
| Calcium | Calcium expressed as Ca; mg/L-as-Ca. |
| Magnesium | Magnesium expressed as Mg; mg/L-as-Mg. |
| Alkalinity | Total alkalinity as CaCO3 equivalent; mg/L-as-CaCO3. dKH/meq/L and conversions deferred until reviewed. |

Candidate concentration/alkalinity values are nonnegative, with six decimal places and the technical upper envelope; exact/belowDetectionLimit/aboveDetectionLimit qualifiers are supported. pH uses the signed technical envelope. A limit qualifier stores the numeric detection limit, not an invented exact value. No recommended aquarium range is used to reject an unusual reading. Numeric resolution is a maximum input precision, not a claim about test-kit accuracy.

The owner accepted the presented reporting bases, units, precision, bounds and qualifiers under SPEC-03. Actual test-kit compatibility still needs verification; identify missing variants where necessary (for example TAN expressed as NH3 rather than N) and seek review of any scientific change. The baseline does not infer a kit's basis from the label ammonia/ppm. USGS [water-quality reporting examples](https://pubs.usgs.gov/sir/2015/5080/) illustrate explicit nitrogen/phosphorus bases and censored measurements; they do not validate this application catalogue. No advice, safe-range or dosing rule is supplied.

## Configuration and Local bootstrap specification

The [nonsecret configuration template](../development/stage-2-configuration.example.json) contains placeholders only. API/worker identities remain independent. Real IDs, endpoints, certificates and grants come from handover; labels/key prefixes are not security boundaries.

| Local component | Proposed address / handling |
| --- | --- |
| Angular SPA | http://localhost:4200; exact registered localhost redirect. This exception is Local only. |
| Aquarium / Tracking | https://localhost:7101 / https://localhost:7102; trusted development HTTPS certificate; exact Local CORS origin, no wildcard credentials. |
| SQL Server Developer | 127.0.0.1:1433; dedicated persistent volume; bootstrap/migration elevation separate from runtime Aquarium schema access. Bind published ports to loopback. |
| Cosmos emulator | https://localhost:8081; explicitly trust the emulator certificate in the development client trust path. SDK gateway mode initially; prove support, no general certificate-validation bypass. |
| Identity | Real Development External ID for customer auth/OBO; individual developer Entra login for approved Azure data/config access. No copied deployed identity. |
| OBO certificate | Separate Local registered certificate; private key outside checkout/User Secrets reference, restricted file access. Development certificate in Key Vault. Never include either private key in browser settings. |

Planned fresh-machine procedure for the later authorised Local setup task:

1. Verify x64 host/virtualisation, supported Linux container engine/Compose, the pinned SDK/Node/npm, development HTTPS certificate, trusted emulator TLS and scoped developer Azure login. Record versions and host compatibility; obtain any required software/licence approval separately.
2. Obtain nonsecret tenant/client/scope/resource identifiers and approved grants from handover. Register exact Local redirect and OBO public certificate. Supply unavoidable secrets through User Secrets/untracked environment, including SQL bootstrap/emulator credentials; committed example files must contain no values.
3. Start only pinned SQL/Cosmos dependencies with health checks and persistent volumes. Publish to loopback. Wait for readiness, apply only authorised Aquarium migrations and Tracking container definitions (/tankId), then load a small reviewed synthetic seed set. Reset must explicitly target these Local volumes and require deliberate destructive action; never point reset at Azure.
4. Restore locked application dependencies and run UI/APIs directly through their development tools. Actual project paths and startup/seed commands are supplied when those projects are authorised and created; they do not exist yet. Do not fabricate runnable application instructions now.
5. Verify explicit profile completion, owner tank access, selected definitions, valid panel/retrieval and rejection of wrong owner/units/revisions. Prove Cosmos atomic panel/idempotency/outbox persistence, duplicate retry behaviour, and no writes when Aquarium/OBO fails. Feature tests are delivered with features, not claimed by this specification.
6. Record emulator limitations and run required approved Development checks for real identity/grants/network/transactions. Share safe results only; no tokens, private notes or credentials in logs. No broker/Advisor/photo workload is required for this bootstrap.

Configuration policy remains startup load and controlled restart; initial candidate OBO/validation total request deadline is 10 seconds with one retry only for safe transient transport/429/5xx failures within that budget, never for authentication/permission/schema failures. Respect Retry-After only within the deadline; otherwise return the accepted temporary failure. These concrete timings are proposed. No retries after a known committed write without its idempotency semantics. Configuration precedence proposal: committed nonsecret defaults, environment-specific nonsecret settings, authorised App Configuration, then explicitly scoped Local User Secrets/environment overrides; never let deployed local-development overrides replace protected settings. Document the chosen provider wiring before implementation. Required missing/invalid settings fail Not Ready; no insecure fallback.

## Platform handover checklist (inputs, not provisioning authority)

- Deployment revision, actual resource IDs/region/SKU, ownership and available capacity for existing plan, SQL ReferenceProjectsDb, Cosmos ReferenceProjects, monitoring and required APIM/ACR/configuration/secrets services.
- API hosting/runtime/container/Always On feasibility; effective APIM/workload/deployment/probe addresses and narrow access rules; development SPA origin and callback URLs.
- Enforceable Aquarium schema and Tracking container access, separate runtime/deployment/developer grants, managed identity IDs, OBO certificate references/rotation, scoped registry/configuration access and negative access tests.
- PP provisions its exclusive service-isolated App Configuration stores and Key Vaults when PP Bicep is altered (accepted ADR-031); verify effective service isolation and grants there. These instances are not a platform-owned provisioning prerequisite.
- Telemetry access/retention and responsible operator; approved child-resource scopes, recovery ownership and resource cost authorisation before cloud mutations.

Unused PostgreSQL/photo infrastructure, Service Bus entities/worker workloads, Test/Production, commercial load tests and public release controls are outside this first-slice preparation. Shared-platform resource creation/verification remains a subsequent explicitly scoped task.

## Verification and remaining gates

Run structural checks from the repository root using a temporary tool dependency directory (PowerShell example):

```powershell
$readinessTools = Join-Path $env:TEMP 'parameter-pilot-readiness-validation'
python -m pip install --target $readinessTools -r scripts/readiness-requirements.txt
$env:PYTHONPATH = $readinessTools
python scripts/verify-readiness-contracts.py
git diff --check
```

The verifier checks the Draft 2020-12 meta-schema, seed shapes/unique IDs/family coverage and valid/invalid structural examples, using decimal-aware JSON parsing and format validation. It makes no Azure call. This is not an application integration, scientific correctness, security or deployment test.

Observed on 29 October 2026: schema meta-validation, all 12 seed shapes and 42 structural cases passed with Python 3.14 and jsonschema 4.25.1; configuration JSON parsed; relative file-link targets in all eight affected Markdown documents existed; `git diff --check` passed. The validator was installed in a task-specific temporary directory, not as an application dependency. No application restore/build, emulator/container execution, scientific validation, Azure/resource inspection, pipeline execution or deployment was performed. Full HTTP/OpenAPI validation and the semantic/runtime checks listed above remain outstanding.

Item 1 preparation and the presented baseline decisions are accepted under the 29 October record. Scientific baseline review is closed for the presented 12 variants; no installation or scientific validation test is claimed. Before Stage 1 closes: actual Local/dev bootstrap, resolved dependency lockfiles/build results, scoped identity/platform handover, CI/delivery/telemetry evidence and Stage 2 acceptance remain outstanding under the readiness guide. Reopen a focused decision if compatibility checks or actual test-kit requirements reveal a material conflict.
