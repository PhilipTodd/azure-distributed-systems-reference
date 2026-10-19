# Security architecture

Version: 0.2 | Date: 19 October 2026 | Status: Proposed

## Identity

Angular uses Entra External ID authorisation-code flow with PKCE for an API access token. APIM validates applicable token requirements; each API independently validates issuer, audience, signature, lifetime and scopes. Map trusted identity claims to an internal user; email is not an ownership key.

Enforce tank access at every resource operation. Workloads use managed identity and narrow roles. Workload authentication does not authorise arbitrary owner data; delegated actor/tank context must be verifiable. Operator access is separately controlled/audited. Final scopes, claims and delegation require an identity ADR.

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
