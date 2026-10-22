# Asynchronous processing and service-owned workers

Version: 0.4 | Date: 21 October 2026 | Status: Accepted design baseline; implementation settings TBD

Approval: [ASYNC-01–08](../engineering/authorised-decisions-2026-10-20.md). Canonical diagrams remain in [Structurizr](structurizr/workspace.dsl).

## Write and read semantics

Tank/configuration, measurement, maintenance and observation CRUD is synchronous: validate/authorise -> local state plus outbox transaction -> success. Reads query the owning store, so a saved record does not wait for messaging before becoming readable. Concurrent edits/ETags and duplicate submissions remain contract requirements.

A committed write can succeed while Service Bus is unavailable. The owner's outbox relay is a timer/change-feed function, not a Service Bus-triggered loop that needs the unpublished message to start. Relay after broker acceptance can still repeat after a crash; idempotency is mandatory.

Advice generation and photo processing use durable asynchronous jobs. Return 202/status Location after durable acceptance; show pending/running/terminal states. A future bulk-ingestion feature needs separate acceptance, job status and backpressure requirements; it is not first-release scope.

## Worker responsibilities

| Function App | Owned stores | Initial functions / later work |
| --- | --- | --- |
| Aquarium Async Worker | Aquarium SQL | Outbox relay; approved Aquarium deferred tasks/integrations/projections when introduced |
| Tracking Async Worker | Tracking Cosmos and Blob | Outbox relay; photo command consumer producing accepted WebP derivatives; Tracking-owned status/history |
| Advisor Async Worker | Advisor PostgreSQL | Outbox relay; advice command consumer; scoped context APIs, pgvector retrieval, Foundry inference, result/quota/snapshot persistence |

APIs/worker functions share their service's domain/application rules where appropriate, not another service's persistence. Aquarium/Advisor must not append directly to Tracking's history store. A genuine Tracking projection may consume a published event into Tracking-owned data; no such projection is required without a product use case.

## Terminology

Tracking History Store (formerly Parameter Event Store) holds product history. Integration events travel through Service Bus/outboxes. Diagnostics go to observability. Neither history records nor delivery logs establish full event sourcing.

## Namespace and entity map

One namespace; the following logical entity names are draft contracts, not deployed infrastructure:

| Entity | Sender | Receiver |
| --- | --- | --- |
| aquarium-events topic | Aquarium outbox function | Consumer-specific subscriptions only for justified use cases |
| tracking-events topic | Tracking outbox function | Consumer-specific subscriptions only for justified use cases |
| advisor-events topic | Advisor outbox function | Consumer-specific subscriptions only for justified use cases |
| tracking-photo-commands queue | Tracking outbox function | Tracking photo function |
| advisor-advice-commands queue | Advisor outbox function | Advisor advice function |

GenerateAdvice.v1 and ProcessPhoto.v1 are addressed commands. PhotoUploadCompleted.v1 is a fact; do not use both event and command as independent duplicate starts. Other service command queues are added only for approved tasks. Aquarium supports service-addressed handlers when needed; no dummy queue handler is required initially.

Each subscription gets an intentional event/version filter. Multiple worker instances on the same queue/subscription compete; subscribers needing a copy each require separate subscriptions. Scope send/listen/manage permissions by entity where supported.

## Recovery and backpressure

Persist outbox until safely delivered; deduplicate consumers by stable message/event ID; commit local inbox/state atomically where possible. For long photo/model work, use bounded execution leases, lock renewal and resumable/idempotent handling. Exact timeout, concurrency, prefetch and delivery settings remain TBD.

Use bounded transient retries; dead-letter permanent/exhausted failures with safe reason codes. Replays preserve identity and record operator/reason/outcome. Protect original request snapshots and personal data in payloads/logs. No global order or exactly-once external AI/accounting effect is claimed.

## Hosting and scale tradeoff

Three Function Apps initially target the existing shared-platform dedicated App Service Plan. Before deployment verify actual plan ownership, OS/SKU, runtime/extensions, capacity, deployment permissions and Always On. Do not describe it as consumption billing or automatic per-queue independent compute scaling.

Shared compute can suffer noisy-neighbour contention across workers and other hosted apps. Bound photo CPU/memory, model concurrency and DB connections; monitor queue age, job duration and API latency. Define measurable thresholds during load testing for moving an app to separate approved compute. Sharing is a cost-conscious starting point, not a claim of high-volume capacity.

## Telemetry

Every API and worker emits OpenTelemetry directly. Propagate W3C context through message properties, distinguish event/message IDs, and link retries/replay to causation. Do not create a Service Bus tracing queue just to emit logs.

## Acceptance evidence

- Broker outage after synchronous write: saved data readable and outbox pending.
- Publish then crash: duplicate delivery has one business outcome.
- Topic fan-out and filter tests: intended subscribers get copies; unrelated workers do not.
- Cross-store negative RBAC tests for all worker identities.
- Retry/lease/poison/DLQ/replay verification without losing source data.
- Slow image/model job under load does not violate agreed API targets; shared capacity constraints reported.
- Restore restores local state/outbox/inbox and prevents duplicate commercial side effects.

[Functions Dedicated hosting](https://learn.microsoft.com/en-us/azure/azure-functions/dedicated-plan) documents Always On requirements and plan sharing. [Service Bus queues/topics/subscriptions](https://learn.microsoft.com/en-us/azure/service-bus-messaging/service-bus-queues-topics-subscriptions) documents competing consumers and fan-out.

## Accepted workload/actor authorisation

ADR-009 accepts managed identities for worker service access plus trusted originating user/tank references. Before protected work/result release, obtain required owner/entitlement checks; service identity alone never grants arbitrary tank access. Actor references come from validated server-side request context, not unsigned browser inputs. No bearer tokens in persistent messages or diagnostics. Customer token and workload token contracts differ; allowed issuer/audience/app-permission and delegation mechanism must be specified before implementation. Dependency failure leaves work recoverable without unauthorised action.

## Accepted durable job context

ID-13/[ADR-009](decisions/adr-009.md): API checks customer/tank access before saving a service-owned job with internal actor/tank/operation and relevant immutable inputs, atomically with its local outbox. The command references this authoritative job. Worker managed identity authenticates the workload; the owning worker loads its own job and checks consistency. Restrict senders and reject forged/inconsistent references; message actor fields are not sufficient authority. Never persist customer bearer tokens.

Before protected work, check current access and applicable entitlements through Aquarium; retry recoverably on temporary unavailability and stop protected work on revoked access. Independently authorise result retrieval. Exact workload endpoints/permissions and long-running check boundaries remain pending. Publication of a fact already committed, such as a measurement event, can continue without reauthorising the original write; it cannot itself authorise new protected work.

## Internal worker operations

ID-14/[ADR-009](decisions/adr-009.md): dedicated internal worker APIs enforce workload caller/operation permission and trusted actor/tank/action checks under ID-13. Aquarium checks current access/entitlements; Tracking supplies authorised Advisor history at Stage 5. No neighbour-store access or blanket authority. Exact contracts/settings remain pending. API-025 remains synchronous OBO.
