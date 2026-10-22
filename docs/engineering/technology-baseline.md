# Accepted technology baseline

Version: 0.3 | Date: 21 October 2026 | Status: Accepted majors/approach; exact pinning and compatibility pending

Authority: accepted [ADR-028](../architecture/decisions/adr-028.md).

| Area | Accepted baseline | Still verify/select |
| --- | --- | --- |
| APIs | .NET 10 / ASP.NET Core 10; C# 14 | SDK/runtime patches, base-image/OS compatibility |
| Relational persistence | EF Core 10 for Aquarium SQL and Advisor PostgreSQL | Compatible provider versions/licensing, migrations/schema settings |
| Functions | .NET isolated worker targeting agreed .NET 10 baseline subject to verification | Functions runtime/extensions/hosting support on actual shared plan |
| Tracking persistence | Azure Cosmos DB .NET SDK, inside Infrastructure | Exact SDK and change-feed/transaction/query settings |
| UI | Angular 22, strict TypeScript/templates | Supported compatible Node.js/TypeScript/Angular patch versions |
| UI structure/rendering | Feature-oriented standalone components, client SPA on SWA | Exact feature/module/folder organisation; no initial SSR |
| UI unit/component tests | Vitest + Angular TestBed | Compatible runner/tool versions |
| Backend tests | xUnit; risk-based layers and applicable passing PR gates (ADR-030) | Backend assertion library/licensing and exact tooling |
| Browser tests | Playwright Test / TypeScript; Chromium PR critical journeys, broader Firefox/WebKit before release | Compatible runner/browser pins, fixtures, report protection and CI setup |
| Dependency policy | Pin SDK/packages/tooling; commit frontend lockfile; reviewed supported patch PRs; no previews by default | Establish actual pins/check commands before implementation |

Do not interpret approved majors as installed/verified versions. Keep provider and Functions support as explicit gates; no silent downgrade/provider substitution. Cosmos SDK selection does not change accepted /tankId, panel/outbox atomicity or database ownership.

Clean Architecture (ADR-002) keeps vendor clients out of Domain and Application implementations; narrow interfaces describe the needed behaviour. API/worker code shares service-local use cases rather than sharing domain libraries across services.

Component/chart libraries, numeric quality gates, backend assertion library and exact dependency inventory remain separate choices.

Sources checked during the Q&A: [.NET policy](https://dotnet.microsoft.com/en-us/platform/support/policy), [.NET 10](https://learn.microsoft.com/en-us/dotnet/core/whats-new/dotnet-10/overview), [Cosmos outbox](https://learn.microsoft.com/en-us/azure/architecture/databases/guide/transactional-out-box-cosmos), [Angular releases](https://angular.dev/reference/releases), [Angular compatibility](https://angular.dev/reference/versions), [Angular testing](https://angular.dev/guide/testing). Pin/reverify exact supported versions at implementation readiness; this file is not an automated compatibility report.

Testing scope and gates: accepted [ADR-030](../architecture/decisions/adr-030.md) and [testing strategy](testing-strategy.md). No blanket coverage percentage initially.

## Minimum Stage 2 Local setup — accepted 21 October 2026

DEV-03: minimum Stage 2 Local setup runs Angular UI and Aquarium/Tracking APIs directly through development tooling. Docker Compose starts SQL Server Developer and Cosmos DB NoSQL emulator containers; use a small repeatable synthetic seed set. Actual Development External ID supports customer authentication/OBO. Select/pin supported compatible container/tool versions after verification; no preview assumption or floating latest pin. Local certificate and secrets follow ID-15/ADR-027.

Emulator/container results are not proof of Azure parity. Verify required operation support, including same-container/partition transactions, and real Development identity/permissions/cloud behaviour. If a required operation is unsupported locally, use the approved Development dependency for that check rather than building an inaccurate substitute. No unapproved resource creation/spend implied.

Advisor/PostgreSQL/photo dependencies wait for their stages. Add Service Bus and workers when the authorised implementation slice requires them; preserve core synchronous transaction/outbox design and do not fabricate broker-delivery evidence. Docker Compose manages dependencies, not a requirement to containerise local UI/APIs. No Compose file, dependencies, seeds, projects or resources created in this documentation update.
