# API catalogue

Version: 0.2 | Date: 19 October 2026 | Status: Draft

All routes below are relative to `/api/v1`.

| ID | Method / route | Contract intent |
| --- | --- | --- |
| API-001 | POST /tanks | 201; name/type/timezone; owner server-derived |
| API-002 | GET /tanks | Owner-scoped cursor list |
| API-003 | GET/PATCH /tanks/{tankId} | Profile; mutation requires ETag |
| API-004 | GET/POST /tanks/{tankId}/parameter-definitions | Built-in/custom definitions |
| API-005 | POST /tanks/{tankId}/measurement-panels | Atomic panel; idempotency required |
| API-006 | GET /tanks/{tankId}/measurements | Parameter/from/to/cursor filters |
| API-007 | POST /tanks/{tankId}/measurement-panels/{panelId}/revisions | If-Match and correction reason |
| API-008 | DELETE /tanks/{tankId}/measurement-panels/{panelId} | Logical deletion; If-Match |
| API-009 | GET/POST /tanks/{tankId}/maintenance-tasks | Plan/query |
| API-010 | POST /tanks/{tankId}/maintenance-tasks/{taskId}/completion | Idempotent transition + historical event |
| API-011 | GET/POST /tanks/{tankId}/maintenance-events | History |
| API-012 | GET/POST /tanks/{tankId}/observations | Notes/changes history |
| API-013 | POST /tanks/{tankId}/dose-calculations | Reviewed formula and inputs |
| API-014 | POST /tanks/{tankId}/photos | Binary upload through Tracking; 5,242,880 file bytes max; 202 + status Location; 413 on excess |
| API-015 | Reserved — former browser completion route withdrawn | Tracking knows upload outcome; no second browser completion call |
| API-016 | GET /tanks/{tankId}/photos/{photoId} | Status; scoped ready download |
| API-017 | POST /tanks/{tankId}/advice-requests | 202 and job Location |
| API-018 | GET /tanks/{tankId}/advice-requests/{requestId} | Scoped job/result plus immutable submitted parameter snapshot |
| API-019 | GET /me/entitlements | Server-derived access/usage |
| API-020 | POST /billing/checkout-sessions | Provider-specific design TBD |
| API-021 | POST /integrations/payments/webhook | Provider authentication, not owner token |
| API-022 | POST /me/exports | Proposed asynchronous export |
| API-023 | POST /me/deletion-requests | Proposed asynchronous deletion |

Before implementation add complete operation schemas/responses, task update/cancel, definition retirement, account cancellation, photo association/delete and accounting contracts. These omissions are tracked readiness work, not implemented endpoints.

## Accepted advice-history route

| ID | Method / route | Contract intent |
| --- | --- | --- |
| API-024 | GET /tanks/{tankId}/advice-requests | Owner-scoped history list, newest first, stable cursor pagination for scroll-back |

API-014 requires bearer auth, per-tank/event checks and idempotency. Define bounded multipart envelope separately from the exact file limit. Missing/misleading Content-Length never bypasses actual-byte enforcement. Interrupted or oversized uploads leave no accepted photo/job; reconcile partial storage failures. API-016 exposes Uploaded/Processing/Ready/Rejected/Failed and authorised ready derivatives. Full request/error schemas remain a readiness gate.

API-017 accepts no photos, image URLs or image embeddings. API-018 returns submitted parameter values/units/times from PostgreSQL snapshot, not live records.
