# Shared Platform readiness evidence — 30 October 2026

Status: Read-only inventory completed; platform readiness gate remains open.

Scope: current Azure subscription and owner-managed platform definitions for the accepted Stage 2 Aquarium/Tracking baseline. No deployment, resource/configuration/role change, application data access, secret/key retrieval or platform source edit was performed. Other projects' resources were identified only to establish sharing and capacity; they are not reassigned to Parameter Pilot.

## Evidence context

- Subscription: Visual Studio Professional Subscription, `9671ac36-9800-451a-b283-35ea87f8b419`, Enabled.
- Platform resource group: `rg-platform-dev`, Australia East resources.
- Platform checkout: `C:/Git/azure-reference-platform`, HEAD `5221bb706bc1290e84414e8bcbaee0acf20bf4b3`; clean at inspection. The checkout is not proof of the deployed Git revision.
- Latest platform-named subscription deployment observed: `platform-dev-3-1`, Succeeded, 3 August 2026 06:52:46 UTC; template hash `12445366627577107586`, correlation `775fb869-7061-4827-b901-6aae3b877b46`. App-owned platform child deployments dated 24 August were also present. No deployed Git SHA mapping was established.
- Metrics: preceding 24-hour windows queried during inspection; plan hourly buckets observed from 28 October 22:39 UTC through 29 October 21:39 UTC (29 October 09:39 through 30 October 08:39 Sydney). These observations are not load tests or capacity guarantees.
- Resource list covered the current subscription under the existing login. It does not establish absence in other subscriptions or tenants, nor authorise their use.

Resource IDs below use prefix `P = /subscriptions/9671ac36-9800-451a-b283-35ea87f8b419/resourceGroups/rg-platform-dev/providers/`.

## Verified existing resources

| Resource | Actual ID suffix after P | Observed state/settings | Remaining acceptance evidence |
| --- | --- | --- | --- |
| Shared App Service Plan | Microsoft.Web/serverfarms/asp-platform-dev | Ready, Linux/reserved, B1, one worker, four sites | Incremental Aquarium/Tracking memory/CPU budget, container pull/start and isolation; no assumption of spare capacity. |
| SQL server | Microsoft.Sql/servers/sql-adt-platform-dev | Ready; public network enabled; TLS 1.2 | Entra administrator/identity setup and enforceable Aquarium schema/runtime/migration access; no SQL session was opened. |
| SQL database | Microsoft.Sql/servers/sql-adt-platform-dev/databases/ReferenceProjectsDb | Online; Basic, 5 DTU; 2 GiB max; Geo backup redundancy | Aquarium schema inventory, effective grants, usage/failure/restore tests and restore owner. |
| Cosmos account | Microsoft.DocumentDB/databaseAccounts/cosmos-adt-platform-dev | Session; free tier enabled; periodic backup; public access enabled, no IP rules; local auth enabled | Enforceable scoped roles, connection/network tests, throughput headroom and restore ownership. Free-tier flag is not a bill or entitlement guarantee. |
| Cosmos database | Microsoft.DocumentDB/databaseAccounts/cosmos-adt-platform-dev/sqlDatabases/ReferenceProjects | 400 RU/s shared manual throughput | Tracking-owned container/index/partition definitions and scoped grants remain absent/unverified. |
| Service Bus | Microsoft.ServiceBus/namespaces/sb-adt-platform-dev | Active; Standard; TLS 1.2; public access and local auth enabled | Do not create unused entities/workers for Stage 2; scoped future slice access remains separate. |
| Log Analytics | Microsoft.OperationalInsights/workspaces/log-platform-dev | PerGB2018, workspace retention 30 days; public ingestion/query enabled | Per-table policy and access verification; workspace default does not establish effective table retention. |
| Application Insights | Microsoft.Insights/components/appi-platform-dev | LogAnalytics ingestion, linked to the above workspace; component retention property 90 days | AppRequests/AppTraces/AppExceptions/AppDependencies each have effective retention and total retention 90 days. Owner-coordinated policy reconciliation needed. |

Parameter Pilot's `stapp-adt-parameterpilot-dev` already exists in `rg-parameterpilot-dev`, East Asia, Free tier. Existence is verified; current content, identity and delivery readiness were not tested. Do not create a duplicate or silently relocate it to Australia East.

## Shared compute and data capacity

The plan currently hosts `api-adt-ticketing-dev`, `api-adt-blastplanning-dev`, `web-adt-blastplanning-dev` and `func-adt-blastplanning-dev`. All were reported Running. The existing Function App reports `DOTNET-ISOLATED|10.0`, Always On true, minimum TLS 1.2. This demonstrates an existing .NET 10 isolated/Always On configuration on this plan; it does not prove that Parameter Pilot's future image, extensions, identity or workload will run correctly. The Azure Linux runtime catalogue also advertises .NET 10.

Plan CPU hourly averages were approximately 20.7–31.0%, with a maximum sample of 99%. Memory hourly averages were approximately 77.8–79.2%, with a maximum sample of 93%. Capacity is not accepted for additional API apps from this snapshot. Do not increase SKU/worker count, stop other applications or change their settings without a scoped platform-owner decision and cost authorisation.

SQL reported maximum DTU consumption 0% and storage 1% in its queried window. That indicates low reported use during that window, not permission or future capacity proof. Cosmos NormalizedRUConsumption returned zero samples; RU headroom is unknown, not zero usage or unlimited capacity. `ReferenceProjects` contains an existing `blastplanning-events` container partitioned on `/streamId`; no Tracking container was returned. Preserve that other-project container and the accepted Tracking `/tankId` boundary.

## Missing first-slice platform prerequisites

Neither the platform Bicep modules nor current subscription resource inventory contains APIM, ACR, Key Vault or App Configuration. Their deployment, tiers, names, networking, scopes and cost approval need a concrete platform change proposal before creation. Platform ownership is already accepted; existence and deployability are not.

No Parameter Pilot API/Function apps or their corresponding runtime managed identities were returned by the subscription resource inventory. These are application-owned resources and must not be confused with platform-managed prerequisites. Provision only when their authorised delivery slice requires them. Future photo Blob/Advisor PostgreSQL resources are not Stage 1 blockers; an existing other-project storage account is not an approved shared replacement.

## Access and security findings

1. SQL Entra administrator list is empty. Managed-identity/individual Entra SQL access and Aquarium schema permissions are not ready for acceptance. The firewall includes the Azure-services-wide `0.0.0.0` rule and a developer address. No password, SQL data or private address was saved here. Do not remove a shared rule until other-project dependencies and a replacement path are reviewed.
2. Cosmos SQL data-plane role assignment list is empty. Account-level keys remain enabled; none were retrieved. Effective Tracking/developer access and cross-container denial are unverified. Shared database membership and naming do not establish isolation.
3. Inherited platform management assignments include a subscription Owner user and three subscription Contributor service principals. These are not evidence of scoped Parameter Pilot deployment or runtime grants; no existing broad assignment was removed or reused. Deny assignments, group membership, eligible elevation and effective data-plane access were not exhaustively audited.
4. App Configuration/Key Vault service isolation must be resolved before provisioning. A single App Configuration store with prefixes/labels is not evidence of isolation. Microsoft's [App Configuration role documentation](https://learn.microsoft.com/en-us/azure/azure-app-configuration/concept-enable-rbac) describes store data reader/owner access; a narrower enforceable design must be demonstrated or separate stores proposed for approval. [Key Vault RBAC](https://learn.microsoft.com/en-us/azure/key-vault/general/rbac-guide) supports individual-object assignments in limited scenarios but recommends careful scoping. No isolation topology is selected by this report.
5. Actual APIM outbound addressing, narrow backend ingress restrictions, SCM/deployment/probe paths, ACR pull permissions, OIDC grants and certificate access cannot be verified while the required resources/identities are missing.
6. Diagnostic retention differs from the accepted target: four main App Insights tables are 90 days despite the workspace's 30-day default. Shared consumers must be reviewed before any change. No retention configuration was altered.

## Required follow-up in order

| ID | Work needed | Gate/status |
| --- | --- | --- |
| PLATFORM-READY-01 | Agree capacity approach for the two initial APIs on the already-used B1 plan, with representative memory/startup estimates and a controlled verification plan. | Human decision if SKU/capacity/spend changes; no scale operation performed. |
| PLATFORM-READY-02 | Specify enforceable Aquarium/Tracking configuration/secret isolation and APIM network feasibility; identify affected ADR-026/027 and Structurizr deployment models if topology changes. | Focused approval before a change to accepted stores/network boundaries. |
| PLATFORM-READY-03 | Prepare platform Bicep/parameters for required APIM/ACR/configuration/secrets resources, concrete tiers/costs/scopes and a reviewed what-if. | Shared-platform edits/deployment need applicable owner authorisation; inventory alone is not deployment approval. |
| PLATFORM-READY-04 | Configure approved SQL identity administration and scoped schema/container/deployment/developer grants; preserve other-project access. | Actual access tests, including denied cross-service/administrative operations, remain required. |
| PLATFORM-READY-05 | Reconcile effective telemetry retention with the 30-day target and record monitoring/recovery owners. | Shared policy approval and post-change verification pending. |
| PLATFORM-READY-06 | Verify provisioned resource IDs/endpoint references, plan startup/network/config access, immutable image pull and required real-Azure behaviour; record deployed revision and handover. | Do not close Stage 1 on management-plane existence alone. |

The next useful deliverable is a concrete platform change proposal addressing these findings. Inventory is complete for this pass; creation and operational verification remain outstanding.

## Read-only checks and limitations

Successful checks: Azure login/subscription context; subscription resource list; plan/raw resource properties; web and Function App metadata; Function runtime/Always On; SQL server/database/firewall/admin metadata; Cosmos databases/containers/throughput/data-role assignments; Service Bus; deployment history; inherited management role metadata; plan/SQL metrics; Cosmos metric query (no samples); workspace/component/table retention; Linux runtime catalogue.

The first CLI attempt could not write its local session cache in the restricted execution context; the permitted host-context retry succeeded. An initial SQL metrics query hit Windows command quoting, and the corrected query succeeded. The convenience plan command returned null for several properties; direct ARM properties supplied Ready/Linux/four-sites. These are resolved collection issues, not resource failures. No failed deployment from historical logs was treated as a current service outage.

Not verified: deployed Git revision, SQL schema/data-plane permissions, workload/developer authentication, cross-owner/container/config isolation, customer External ID/OBO, actual API traffic, container execution, application latency, restore, Cosmos RU utilisation, future capacity or resource costs. No secrets/keys/tokens or customer records were retrieved. This report does not complete Stage 1 or authorise implementation/deployment/merge.
