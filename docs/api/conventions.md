# API conventions

Version: 0.2 | Date: 19 October 2026 | Status: Proposed

- Prefix `/api/v1`, JSON and bearer access tokens.
- Owning services enforce resource access independently of APIM.
- RFC 9457 `application/problem+json`, stable code and trace ID; no internal details.
- RFC 3339 UTC output timestamps; accept explicit input offsets.
- Opaque cursors: default 50, maximum 200; stable effective-time/ID ordering.
- ETag/If-Match on mutable resources; stale condition returns 412.
- Required Idempotency-Key on retryable creations/commands; scope actor + operation + tank + key.
- Same key/equivalent payload returns original outcome; different payload returns 409.
- Proposed idempotency retention seven days, advertised to clients. Domain transitions remain duplicate-safe after key expiry.
- 400 malformed request; 401 invalid/missing authentication; 404 inaccessible/nonexistent resource; 422 semantic validation; 429 quota/rate limit; 503 dependency unavailable.
- Entitlement 403 only after ownership established.
- No arbitrary database filters or unbounded scans.
- Breaking versions require migration; additive optional fields must not break tolerant clients.

Full contracts are slice-readiness gates. Markdown excerpts are not evidence of schema validation or implementation.

## Accepted photo upload exception

Photo binary ingress is through Tracking at API-014, not JSON or direct-to-Blob. Enforce the exact file limit 5,242,880 bytes; allow separately bounded multipart overhead. Return 413 for excess and 202 with status Location for durable accepted work. No separate browser completion call. Download authorisation is independent from upload.
