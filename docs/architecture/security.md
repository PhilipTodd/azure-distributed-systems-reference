# Security architecture

Version: 0.17 | Date: 21 October 2026 | Status: Accepted identity approach; other detailed security controls retain their recorded status

## Identity

Angular uses Entra External ID authorisation-code flow with PKCE for an API access token. APIM validates applicable token requirements; each API independently validates issuer, audience, signature, lifetime and scopes. Map trusted identity claims to an internal user; email is not an ownership key.

Enforce tank access at every resource operation. Workloads use managed identity and narrow roles. Workload authentication does not authorise arbitrary owner data; delegated actor/tank context must be verifiable. Operator access is separately controlled/audited. ADR-009 now accepts the identity approach; exact tenant/app/scopes/roles/claims, session/MFA and delegation configuration remain TBD; the initial customer method is accepted below.

## Threat model

| Threat | Control / verification |
| --- | --- |
| Cross-owner access | Resource checks and negative integration tests |
| Forged/replayed billing event | Signature verification, durable deduplication, provider reconciliation |
| Unsafe upload | Quarantine, size/dimension checks, scan/decode and private download |
| Oversized/bypassed UI upload | Authenticated Tracking endpoint, actual-byte 5,242,880 limit, bounded temporary buffering, 413 and cleanup; no browser upload SAS |
| Prompt injection | Untrusted-data boundaries, scoped retrieval, no mutation tools, evaluations |
| Cost exhaustion | Quotas, concurrency limits and global spending controls |
| Shared-platform lateral access | Separate identities and least-privilege data roles |
| CI credential theft | Federation, restricted environments and untrusted-PR isolation |
| Supply-chain compromise | Locked dependencies, scanning, SBOM and image provenance |
| Deleted data restored | Deletion ledger and post-restore reconciliation |

## Integration boundaries

Dedicated payment webhook validates provider credentials instead of owner bearer tokens. Validate signatures over provider-required original request bytes and enforce replay controls. Browser redirect cannot grant premium access. Out-of-order events require reconciliation rather than blindly accepting latest arrival.

Store secrets in Key Vault, prefer identities, restrict CORS, require TLS and review network exposure. Blob storage remains private. No sensitive payloads in diagnostics. Xero OAuth permissions/token lifecycle and accounting retention need dedicated design before integration.

Threat review covers browser/edge, service/service, stores/broker, AI/retrieval and external integration trust boundaries. Record residual risk owner and acceptance; this document is not a completed penetration test.

## Accepted upload enforcement and image-context boundary

The UI check is usability feedback, not security. Tracking enforces actual file bytes, rejects overflow before Blob persistence and cleans temporary data on failure/cancellation. Align gateway/host/request limits with bounded multipart overhead; Content-Length alone is insufficient. Rate/concurrency/timeouts and decoded-image resource limits remain implementation-readiness controls.

Retained originals stay private and potentially contain original metadata; owner deletion/retention policy must account for them. Serve only authorised ready derivatives. Photos, Blob access URLs and image embeddings are excluded from AI context throughout this pack.

[ASP.NET Core upload guidance](https://learn.microsoft.com/aspnet/core/mvc/models/file-uploads) describes streamed uploads/request limits. [SAS specification](https://learn.microsoft.com/en-us/rest/api/storageservices/create-user-delegation-sas) provides permissions/expiry constraints but no per-upload application byte limit.

## Accepted worker baseline — 20 October 2026

See [asynchronous-processing design](asynchronous-processing.md). Service-owned workers use only their owner's stores; core CRUD stays synchronous with local outboxes. Advice/photo handlers are durable asynchronous workflows. One namespace routes relevant commands/events; direct telemetry is not a queued business task. Shared-plan compute requires capacity/concurrency verification.

## Accepted schema/container isolation

Aquarium runtime identities are restricted to Aquarium schema in ReferenceProjectsDb; other schemas are inaccessible. Migration principal/history are scoped separately. Tracking data roles are limited to owned containers in ReferenceProjects. Partition keys do not authorise users; enforce owner checks independently. Test access to other projects' schemas/containers is denied. App deployment permissions to shared scopes require explicit delegation; no database-owner runtime role or platform-wide capacity/policy changes.

## Accepted identity enforcement

Entra External ID customer PKCE flow -> API access token -> APIM validation -> independent API validation. Aquarium owns mapping from validated stable identity to internal user and tank access; email/body/header user IDs are not authoritative. Managed identity secures workload access, not end-user ownership; preserve verifiable actor/tank context and recheck protected work/results as required. Do not persist bearer tokens in messages/logs. Fail closed if required checks/context are unavailable. Detailed customer-token versus workload-token issuers/audiences/permissions and session/MFA settings remain open under accepted ADR-009; initial registration is settled below.

## Accepted Development ingress and secrets decisions

ADR-026: browser API access through APIM only; backend public HTTPS endpoints restricted to verified APIM/required workload sources. Reject other traffic and still validate each token/role/tank operation. Feasibility is conditional on narrow reliable addressing; no region-wide allowlist/CORS/header bypass. Front Door/WAF waits for release preparation.

ADR-027: nonsecret settings/flags in App Configuration; unavoidable secrets in Key Vault; managed identities for deployed reads; local secrets untracked and not assumed encrypted. Never ship secrets to Angular/source/logs/images. Enforce shared-service isolation rather than relying on prefixes/labels; exact access assignments and refresh/rotation/failure implementation settings remain detailed decisions; high-level policies are accepted below.

## Accepted service-level configuration and secret isolation

ADR-027 now explicitly limits Aquarium/Tracking/Advisor API and worker identities to their respective required settings/secrets. Each workload has independent least-privilege grants. Nonsecret settings may be intentionally shared; services do not automatically gain cross-service secret reads.

Deployment configuration-management permissions are separate from runtime readers. Runtime identities cannot administer configuration/secrets; deployment rights do not imply blanket platform/secret access. Verify enforced boundaries with negative access tests. Prefixes/labels alone cannot establish isolation; propose separate stores/vaults for approval if shared hosting cannot enforce it. Exact grants, developer-role assignments and operational policy implementation remain outstanding; accepted approaches are recorded below. See [access matrix](../infrastructure/configuration-and-secrets.md).

## Accepted local identity and operational configuration policies

ADR-029: individual developer Entra identities with scoped dev permissions via approved developer sign-in, no shared account/copied workload credentials, separate administration elevation. Customer External ID sign-in remains distinct.

ADR-027 now accepts startup-only configuration loading/controlled restart, deferred dynamic flags, operator-controlled rotation with verified provider-supported overlap, not-Ready startup on missing required config and bounded retry. Running with loaded config is allowed during config-store outage only while authorisation/downstream access remain valid. No insecure fallback or false-success job acknowledgement. Exact policies' implementation/grants/timers remain to be specified.

## Accepted customer account-isolation safeguards — 21 October 2026

[ADR-009](decisions/adr-009.md) and [ID-06–08](../engineering/authorised-decisions-2026-10-21.md) accept a dedicated customer External ID tenant/tenant-specific ciamlogin.com authority, initial local email-passcode flow and deferred social/federated sign-on. Do not use workforce B2B guest invitations for customer registration.

Same-email personal Microsoft and customer accounts are separate identities. No automatic email-based linking, ownership or Microsoft federation fallback. APIM and each API validate the expected issuer/audience/signature/lifetime/permissions; stable issuer/tenant-qualified identity maps to Aquarium's internal user. Session-domain separation is supporting isolation, not a substitute for token checks.

Display the active customer account and provide sign-out/switch-account. Existing customer SSO may remain; email passcode alone is not MFA. Verify same-browser concurrent Microsoft/customer sessions using the same email, wrong-issuer rejection and no cross-account tank access. Actual session/MFA policy and tenant setup remain pending.

## Accepted customer MFA sequencing

ID-09/[ADR-009](decisions/adr-009.md): no mandatory customer MFA through Stages 1–5. Stage 6 must reassess MFA, account recovery and subscription/billing-change protection before public commercial launch. Revisit earlier if risk/data/capabilities materially change. Administrator/platform protections remain separate. Existing privacy, ownership, token and account-isolation controls remain required; private user data is not classified as nonsensitive by this deferral.

## Accepted customer session handling

ID-10/[ADR-009](decisions/adr-009.md): MSAL Angular uses its supported localStorage token cache; silent acquisition/renewal with interactive fallback. Use supported MSAL sign-out/cache cleanup plus External ID sign-out and coordinate other open tabs/account changes. Cached credentials do not override issuer, audience, expiry, permission or owner validation. Sign-out is not immediate revocation of all issued tokens.

localStorage persistence improves return/multi-tab experience but increases state left on shared devices; it is JavaScript-accessible and requires XSS/dependency protections. Application cache and External ID cookies have separate lifecycles. Hold unsaved measurement input only in memory through same-user reauthentication; clear on different-user sign-in or explicit sign-out. Do not infer persistent draft storage. Exact tenant session durations/policy remain pending.

## Accepted customer API permissions

ID-11/[ADR-009](decisions/adr-009.md): Aquarium and Tracking each expose separate customer delegated read/write permissions. Aquarium.Read/Aquarium.Write and Tracking.Read/Tracking.Write are proposed names; verify exact identifiers/audiences and route policies. Advisor permissions follow at Stage 5. APIM and receiving APIs enforce applicable scopes alongside independent per-tank ownership; API permission is never proof of tank access. Write does not implicitly include Read. Workload permissions remain distinct. Verify insufficient scope, wrong-service token, read-only write and cross-owner denials.

## Accepted synchronous API delegation

ID-12/[ADR-009](decisions/adr-009.md): OAuth OBO carries validated customer delegation through synchronous API chains. Tracking obtains an Aquarium-audience delegated token; Aquarium checks token/permission/calling application and tank ownership. Do not accept Tracking tokens at Aquarium, trust body/header actor claims or fall back to unsigned context after exchange failure. Client-authentication/consent/configuration details still require verification. Async worker managed identities/durable actor context are separate; bearer tokens never enter persistent messages.

## Accepted asynchronous actor context

ID-13/[ADR-009](decisions/adr-009.md) makes server-owned jobs authoritative for actor/tank/operation/input provenance. API validates access before durable job/outbox creation; restricted command references identify that job. Owning workers use managed identities, read only their own jobs, reject inconsistent references and obtain current protected-work access/entitlement decisions through Aquarium. Retry temporary check failures recoverably; revoked access stops protected processing. Result access is checked separately. No customer bearer tokens persist; message fields alone confer no owner access. Fact publication for previously committed operations remains distinct from fresh protected processing.

## Accepted internal workload boundary

ID-14/[ADR-009](decisions/adr-009.md): dedicated worker operations require approved workload callers, operation-specific permissions and actor/tank/action validation. Managed identity is not blanket customer access. Aquarium checks current access/entitlements; Tracking supplies authorised Advisor history in Stage 5. Retain network restrictions/token validation. API-025 remains customer OBO despite its internal URL. Exact contracts/grants remain pending.

## Stage 2 identity configuration — accepted 21 October 2026

ID-15: approve three registrations in the dedicated customer tenant: Parameter Pilot UI, Aquarium API and Tracking API. Each API validates its own audience. Confirm delegated scope names Aquarium.Read, Aquarium.Write, Tracking.Read and Tracking.Write; full scope URIs/registration GUIDs remain actual setup outputs. Aquarium uniquely maps validated tenant ID plus object ID (tid + oid) to internal user ID; do not use email or application-specific sub for cross-API identity matching. Verify required claims and reject missing/untrusted identity context.

Only the approved Tracking application may use OBO for Aquarium panel validation, requiring Aquarium.Read and independent tank ownership. Route policies must also restrict the calling application; a scope alone does not approve all callers. Tracking authenticates as a confidential client using a registered certificate. Protect Development private key in Key Vault; local Tracking uses a separate local certificate outside source control. Select/verify secure supported library loading, private-key permissions, credential rotation and registration of both public certificates; no private key is shipped to the UI. Certificate authentication supplements, rather than replaces, the delegated OBO token.

Register explicit localhost redirect addresses for authorised Local development and explicit Development redirects; no invented/wildcard deployment addresses. Advisor registrations remain deferred. Exact GUIDs/audiences/URIs/redirects/certificate references and supported implementation are setup/verification tasks, not new product choices. No registrations, certificates, grants or settings were created.

Authority: [ADR-009](decisions/adr-009.md).
