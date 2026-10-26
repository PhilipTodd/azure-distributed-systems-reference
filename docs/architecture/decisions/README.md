# ADR catalogue

Version: 0.16 | Date: 26 October 2026 | Status: Mixed — see individual decision records

Canonical ADR directory: `docs/architecture/decisions/`. ADR-001, ADR-002, ADR-003, ADR-005, ADR-006, ADR-007, ADR-008, ADR-009, ADR-011, ADR-012, ADR-015, ADR-016, ADR-018, ADR-021, ADR-023, ADR-024, ADR-025, ADR-026, ADR-027, ADR-028, ADR-029 and ADR-030 are Accepted for their recorded decisions; ADR-004, ADR-017 and ADR-022 are Partially Accepted. Other ADRs remain Proposed. Approval evidence links to the owner's 19 and 20 October 2026 chat decisions.

| ADR | Decision subject |
| --- | --- |
| [ADR-001](adr-001.md) | Three service boundaries |
| [ADR-002](adr-002.md) | Proportionate Clean Architecture |
| [ADR-003](adr-003.md) | Store ownership and cross-service reads |
| [ADR-004](adr-004.md) | SQL and Cosmos responsibilities |
| [ADR-005](adr-005.md) | Cosmos partition strategy |
| [ADR-006](adr-006.md) | History without full event sourcing |
| [ADR-007](adr-007.md) | Reliable publication |
| [ADR-008](adr-008.md) | Messaging and compatibility |
| [ADR-009](adr-009.md) | Customer identity and tank access |
| [ADR-010](adr-010.md) | Entitlement authority |
| [ADR-011](adr-011.md) | API container hosting |
| [ADR-012](adr-012.md) | Service-owned workers |
| [ADR-013](adr-013.md) | Deterministic dosing |
| [ADR-014](adr-014.md) | Foundry inference selection |
| [ADR-015](adr-015.md) | Advisor PostgreSQL persistence and curated retrieval |
| [ADR-016](adr-016.md) | Photo upload, limits and derivative lifecycle |
| [ADR-017](adr-017.md) | Observability and privacy |
| [ADR-018](adr-018.md) | Delivery authority |
| [ADR-019](adr-019.md) | Payment provider |
| [ADR-020](adr-020.md) | Xero release placement |
| [ADR-021](adr-021.md) | Initial tank access model |
| [ADR-022](adr-022.md) | Environments, cost and recovery |
| [ADR-023](adr-023.md) | Aquarium parameter definitions and validated Tracking measurement panels |
| [ADR-024](adr-024.md) | Shared platform ownership, Aquarium schema and Tracking containers |
| [ADR-025](adr-025.md) | Local and Development initially; release environments deferred |
| [ADR-026](adr-026.md) | Development APIM ingress and restricted public backends |
| [ADR-027](adr-027.md) | Configuration, secrets and managed-identity access |
| [ADR-028](adr-028.md) | Backend, Tracking persistence and frontend technology baseline |
| [ADR-029](adr-029.md) | Hybrid Local dependencies and individual developer identity |
| [ADR-030](adr-030.md) | Automated testing and browser verification |

Acceptance requires context/options review, consequences, readiness verification and recorded human approval. Superseded decisions retain links/history. Legacy decision documents remain references until deliberately reconciled.

Accepted/partially accepted ADRs do not approve the whole pack or implementation. See [authorisation record](../../engineering/authorised-decisions-2026-10-19.md).

20 October worker approval: [decision record](../../engineering/authorised-decisions-2026-10-20.md). ADR-016's photo-processing unit is now functions within Tracking Async Worker; accepted derivative rules are unchanged.

21 October identity refinement: [approval record](../../engineering/authorised-decisions-2026-10-21.md); ADR-009 includes local email-passcode registration, deferred social sign-on and same-email Microsoft/customer account-isolation safeguards.

26 October 2026: the human owner explicitly approved the three-service separation; see ADR-001 for the recorded evidence and scope.

26 October 2026: the human owner accepted current records plus immutable revision/audit history and rejected full event sourcing; see ADR-006 and the [26 October approval record](../../engineering/authorised-decisions-2026-10-26.md) for accepted correction, audit, concurrency, retention and scope policies and remaining implementation-readiness work.
