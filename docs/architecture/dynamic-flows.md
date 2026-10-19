# Dynamic flows and consistency

Version: 0.2 | Date: 19 October 2026 | Status: Proposed

## Record panel

1. SPA acquires API access token; APIM and Tracking validate it.
2. Tracking verifies owner and definition revisions through Aquarium.
3. Validate panel and scoped idempotency key.
4. Commit panel, idempotency record and outbox event in one Cosmos container/partition transaction.
5. Return 201 after durable commit.
6. Tracking relay publishes; consumers deduplicate event IDs.

Accepted data survives broker outage. Reads may observe a write before asynchronous consumers catch up.

## View trends

Validate owner; query Tracking by tank/parameter/time using bounded cursor pagination; return explicit units/qualifiers/gaps. Optional maintenance overlays use effective time and do not assert causation.

## Advice

1. Check owner, entitlement and quota.
2. Transactionally reserve usage, persist job and write outbox command; return 202 with Location.
3. Worker acquires expiring lease, rechecks access, collects versioned context and persists the actual submitted parameter snapshot in PostgreSQL.
4. Retrieve approved passages/embeddings from the same Advisor PostgreSQL instance using pgvector; call Foundry without photo context, validate output and persist terminal state.
5. Settle/release quota under approved policy; check access before returning protected result.

Duplicate jobs cannot create duplicate stored results. External inference is not exactly once: a timeout may incur provider cost even when the application retries.

## Photos — accepted upload and processing route

1. UI checks selection size: reject above 5,242,880 bytes with feedback.
2. Browser uploads binary through APIM to Tracking, with authentication and idempotency. No browser Blob SAS or separate browser success/completion call is required.
3. Tracking checks tank/event access and rejects excessive declared size early. It counts actual file bytes in a bounded stream, including when length is absent or misleading; overflow returns 413.
4. Stage no more than the allowed file plus an overflow-detection byte in bounded temporary storage. Do not write an oversized original to Blob. Multipart limits allow bounded envelope overhead separately.
5. Save a within-limit completed original privately, then durably record Uploaded metadata and the service-owned processing work. Handle Blob/Cosmos non-atomicity with reconciliation and reliable publication under the approved event design.
6. Return 202 and a status Location only after upload and durable work registration. API receipt replaces browser completion notification.
7. Tracking's photo worker validates/scans/decodes and respects orientation; produces cropped 400 x 400 WebP thumbnail and padded 1200 x 800 WebP hero, stripping derivative metadata.
8. Retain the original for reprocessing; mark Ready only after both derivatives and metadata are durable. Invalid input becomes Rejected; transient failure is retryable.
9. UI queries status; future gallery uses thumbnail and opens hero. Reconcile abandoned temporary data, orphan originals and partial derivatives.

Processing duplicate notifications is safe. Blob events may support reconciliation, but are not sole proof of a registered/authorised upload. Source-format/pixel limits, compression quality, crop alignment, padding colour and upscaling remain TBD.

## Historic advice — accepted UX

List requests/results with stable cursor pagination; selecting a result rechecks owner access and returns advice plus the original submitted parameter snapshot from PostgreSQL. Later reading corrections do not rewrite that snapshot. Photos never enter the request context.

## Subscription and accounting

Verify provider webhook; durably deduplicate; reconcile provider state when ordering is ambiguous; transactionally update entitlement and outbox. Xero synchronisation is recoverable background work with external references, retry/deduplication and visible reconciliation state. Browser checkout return never grants access.
