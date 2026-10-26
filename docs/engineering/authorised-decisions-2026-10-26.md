# Authorised design decisions — 26 October 2026

Version: 0.1 | Date: 26 October 2026 | Status: Accepted decisions only

## Authority and scope

Evidence is the human project owner's statements in the docs-site update chat on 26 October 2026. These approvals concern recorded design choices and documentation updates; they do not authorise application implementation, deployment, spending, migration or merge.

| ID | Accepted decision | Evidence and primary record |
| --- | --- | --- |
| BOUNDARY-01 | Separate Aquarium, Tracking and Advisor services | "The proposed separation of services is approved." ADR-001 |
| HISTORY-01 | Current records plus immutable revision/audit history; exclude full event sourcing | "I do not want full event-sourcing implemented. I accept the proposed decision." ADR-006 |
| HISTORY-02 | Measurement versioning with Active/Superseded/Deleted states, structured History, stable measurement and unique version identities, linked versions, atomic replacement, retained measurement time unless corrected, active-only current views and preserved advice inputs | Owner proposed the CRUD model, then stated "I accept your proposals above" after refinements. ADR-006 |
| HISTORY-03 | Audit fields and optional reason; stale-write conflict handling and retry deduplication; logical deletion and restoration into a new version; initial indefinite retention with pre-production review; separately controlled permanent erasure; initial measurement-only scope and panel validation | Owner stated "I accept the above proposals. Update the documentation." after the detailed policy proposals. ADR-006 |

## Remaining readiness work

ADR-006 defines the accepted behaviour. Exact physical panel/version representation, executable concurrency/idempotency contracts, capacity and transaction feasibility, and verification remain implementation-readiness work. Review initial retention before production; define permanent-erasure permissions, dependent advice-snapshot handling and actor-identity retention before implementing erasure. Other Tracking record types require separate lifecycle decisions.
