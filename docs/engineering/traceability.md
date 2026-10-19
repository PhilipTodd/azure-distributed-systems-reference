# Traceability register

Version: 0.2 | Date: 19 October 2026 | Status: Draft

Requirement -> story -> design/ADR -> API/event/data contract -> issue -> implementation -> tests/evaluations -> PR -> human approval.

| Requirement | Story | Design | Contract | Verification |
| --- | --- | --- | --- | --- |
| FR-002, NFR-007 | US-007 | ADR-001, ADR-009 | API-001–003 | Lifecycle/owner isolation |
| FR-003–004, NFR-004 | US-001–002 | ADR-004–007 | API-005–008, EVT-003–005 | Units, retries, concurrency, broker outage |
| FR-005–008 | US-003–004 | Domain/time rules | API-006, API-009–012 | Ordering/timezone/completion retries |
| FR-011/014 | US-005 | ADR-014–015; DEC-07–09 | API-017–019/024 | Grounding/isolation/quota/failure; immutable history snapshot; no photo context |
| FR-010 | US-006 | Accepted ADR-016; DEC-04–06 | API-014/016, EVT-007–008; API-015 withdrawn | Actual-byte cap, partial upload, crop/pad WebP, retained original, unsafe/orphan cleanup |
| FR-012–013 | Commercial stories TBD | ADR-010/019–020 | API-020–021; accounting TBD | Signature/order/dedup/reconciliation |
| NFR-006 | US-008 | Recovery plan | Data/runbooks | Restore exercise |

FR-009 dosing and FR-015 export/delete need expanded stories/contracts before implementation. NFR targets link to release verification plans when environments exist. Issues, source/test files, PRs and approval references are intentionally unset. Do not manufacture evidence.

Audit record: task/agent identity, requirements, rationale, checks, compatibility, security/telemetry impact, docs/traceability, reviewer and outcome. Private model reasoning is not an audit artefact.
