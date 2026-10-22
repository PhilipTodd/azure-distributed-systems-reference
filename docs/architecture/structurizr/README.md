# Parameter Pilot - Structurizr Architecture

This directory contains the Structurizr DSL architecture model for the Parameter Pilot application.

The workspace loads the Microsoft Azure 2021 theme. Azure resource tags in `model/systems.dsl` and `model/deployment.azure.dsl` select its icons; `views/styles.dsl` styles the logical application elements. Structurizr Lite needs internet access to load the theme and icons.

## Decision update — 19 October 2026

Authoritative DSL now includes accepted Advisor PostgreSQL/pgvector consolidation, Tracking upload/5 MiB enforcement, Tracking-owned photo processing/WebP derivatives, and Advice history snapshot flow. Approval: [decision record](../../engineering/authorised-decisions-2026-10-19.md). Other candidate architecture remains unapproved where not separately accepted.

**Export status:** Structurizr Lite parsed the updated DSL and regenerated workspace.json during the 20 October service-view update. Existing exported SVGs still predate these changes; regenerate exports before publishing static diagrams. See [remaining reconciliation](../c4.md).

## Run locally

From the repository root, run Structurizr Lite with the directory mounted:

```powershell
docker run -it --rm -p 8080:8080 -v "C:\Git\azure-distributed-systems-reference\docs\architecture\structurizr:/usr/local/structurizr" structurizr/lite
```

Then browse to:

```text
http://localhost:8080/
```

## Views

- System Context
- Containers - Aquarium Service (AquariumContainers)
- Containers - Tracking Service (TrackingContainers)
- Containers - Advisor Service (AdvisorContainers)
- Outbox - Aquarium tank creation (AquariumOutbox)
- Outbox - Tracking measurement recording (TrackingOutbox)
- Outbox - Advisor request and completion (AdvisorOutbox)
- Record aquarium parameter
- View parameter trends
- Generate maintenance advice
- Upload via Tracking and generate WebP images
- Browse historical advice and submitted parameters
- Azure deployment

## Important DSL structure

External software systems such as Microsoft Entra External ID and Stripe are declared at the model/workspace scope, rather than inside the Parameter Pilot software-system declaration. This is required by the Structurizr DSL grammar.

## Worker update — 20 October 2026

Source now models three service-owned Async Workers, local outbox relays, synchronous core writes, scoped owner APIs and asynchronous advice/photo processing. Functions target the existing shared-platform App Service Plan subject to compatibility/capacity/Always On verification. Photo processing is part of Tracking, not a fourth worker. One namespace supplies separate queues/subscriptions; Tracking Cosmos is Tracking History Store. See [async design](../asynchronous-processing.md) and [approval](../../engineering/authorised-decisions-2026-10-20.md).

During the earlier worker update workspace.json was left unchanged. The subsequent service-view preview has now regenerated it from DSL. Static SVG exports still require regeneration.

## Service-focused views — 20 October 2026

The former combined Containers view is replaced by exactly three service-focused container views. All reuse the same canonical elements; the Service Bus shown in each is the same namespace. Neighbour APIs appear only as dependencies; their stores/workers are omitted. Observability remains omitted from these views.

Outboxes are records inside owned databases, not independent deployable containers. Each container description identifies its local transaction/relay, while the three Outbox dynamic views show atomic commit, response, relay, broker acceptance and dispatch bookkeeping. The send/dispatch gap permits duplicate publication and requires stable IDs/idempotent consumers. Existing PhotoUpload and MaintenanceAdvice views show the deferred workloads.

## Measurement-panel validation update

Accepted ADR-023 adds explicit one-batch Tracking-to-Aquarium definition/rule/eligibility retrieval to RecordParameter and TrackingOutbox. UI reads selected definitions from Aquarium; server validation is independent of browser checks. Stale revisions and Aquarium failure produce no panel/outbox persistence. Reload Lite to regenerate workspace.json; exported SVGs require separate refresh.

## Shared data placement update

Accepted ADR-005/024: Aquarium SQL Schema denotes app-owned data within platform-owned ReferenceProjectsDb, not a separate SQL database. Tracking History Store denotes app-owned /tankId containers within platform-owned ReferenceProjects Cosmos database. Deployment view groups shared hosting/namespace/monitoring under Shared Development Platform. Outbox/state atomicity still requires the same container and partition. Reload Lite after source change; do not infer live resources from this model.

## Customer identity view

CustomerIdentity shows accepted ADR-009: customer PKCE/API token, APIM and API validation, Aquarium internal-user/tank authority and fail-closed access. Web-to-External-ID relationship is explicit. No real tenant/apps/roles were configured; exact delegated actor mechanism remains design work. Reload Lite for updated source; exported SVGs need separate refresh.

## Development hosting view

Deployment source now shows separate API apps and worker Functions on shared Linux plan, APIM/SQL/Cosmos/Blob/PostgreSQL/monitoring shared hosting, and Static Web Apps for Angular. This reflects accepted placement/ownership, not deployment. Restrictions need verified APIM/workload addresses; no Front Door/WAF initial dev resource. Configuration/secrets are described in ADR-027 without additional container-view clutter. Reload Lite to regenerate workspace; static SVG exports remain a separate step.

## Accepted technology baseline labels

systems.dsl now labels APIs ASP.NET Core 10/C# 14, UI Angular 22/strict TypeScript and isolated Functions .NET 10 subject to compatibility verification. ADR-028 selects direct Cosmos SDK in Tracking Infrastructure and relational EF Core 10; exact versions/providers/host support remain unverified. No application projects/dependencies installed. Reload Lite to regenerate labels in workspace.json; static exports require separate refresh.
