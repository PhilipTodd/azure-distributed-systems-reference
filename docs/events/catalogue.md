# Event architecture and catalogue

Version: 0.1 | Date: 8 October 2026 | Status: Proposed

| ID | Event | Publisher | Consumer intent |
| --- | --- | --- | --- |
| EVT-001 | TankCreated.v1 | Aquarium | Optional projection |
| EVT-002 | TankAccessChanged.v1 | Aquarium | Approved access-cache holders |
| EVT-003 | MeasurementPanelRecorded.v1 | Tracking | Approved downstream processing |
| EVT-004 | MeasurementPanelCorrected.v1 | Tracking | Derived state |
| EVT-005 | MeasurementPanelDeleted.v1 | Tracking | Derived cleanup |
| EVT-006 | MaintenanceCompleted.v1 | Tracking | Approved downstream processing |
| EVT-007 | PhotoUploadCompleted.v1 | Tracking | Tracking photo worker |
| EVT-008 | PhotoProcessingCompleted.v1 | Tracking | Approved notification/projection |
| EVT-009 | EntitlementChanged.v1 | Aquarium | Advisor |
| EVT-010 | AdviceCompleted.v1 | Advisor | Approved notification/projection |
| EVT-011 | UserDeletionRequested.v1 | Aquarium | All data owners |

GenerateAdvice.v1 is a command on a separate queue, not an event claiming completed work. Catalogue entries do not imply deployed consumers. Detailed deletion completion acknowledgements need design before that workflow.

## Topology and reliability

- Topic per publishing context with consumer-specific subscriptions; dedicated advice command queue.
- Local transactional outbox; at-least-once publication/delivery.
- Consumer inbox and state change committed together where possible.
- External side effects need independent idempotency/reconciliation.
- Entity revisions prevent stale overwrite; no global ordering promise.
- Bounded transient retry with jitter; proposed maximum delivery count ten.
- Poison messages to DLQ; restricted payload inspection.
- Replay preserves event ID and records operator/reason/result.
- Sessions only when ordering requirement justifies them.
- Breaking type/schema version requires migration; additive consumers tolerate unknown fields.
- Private notes/history stay out of events; fetch further context through authorised APIs.
- Dapr deferred; contracts independent of optional broker abstraction.

See [schemas](schemas.md) and [data reliability](../architecture/data.md).
