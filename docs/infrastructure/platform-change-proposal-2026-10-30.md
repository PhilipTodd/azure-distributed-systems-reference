# Shared Platform change proposal — 30 October 2026

Status: Superseded cost/capacity scenario; retained as historical proposal. No deployment authorisation.

Ownership supersession: the owner has now accepted PP ownership of PP-exclusive App Configuration stores/Key Vaults, with deployment when PP Bicep is altered. ADR-031 supersedes this document's platform-managed instance recommendations; do not implement those recommendations in azure-reference-platform.

**Current direction:** retain B1 and include one APIM Developer unit, explicitly required by the owner for education. The [updated budget](development-hosting-budget-2026-10-30.md) supersedes B2 and the incremental A$120 allowance below, and reinstates Developer after its brief cost-driven withdrawal. Whole-subscription run rate plus Developer and planned ACR is approximately A$118.41/month before tax and new variable usage, exceeding the A$80 preference. Do not implement the historical B2 schedule/cost scenario. Other unaccepted topology/access proposals remain pending; keep ADR-026 dedicated-address restrictions and verify actual behaviour before acceptance.

Inputs: [live inventory](platform-readiness-2026-10-30.md), accepted ADR-024/025/026/027 and [Stage 2 baseline](../engineering/stage-2-readiness-specification.md). PostgreSQL remains a platform-owned server for Stage 5, with Advisor-owned database/content. No PostgreSQL, photo Blob, new broker entities, workers, Test or Production resources are requested here.

## Proposed decisions

| ID | Recommendation | Approval/verification boundary |
| --- | --- | --- |
| PLATFORM-PROP-01 | Upgrade existing shared Linux plan from B1 to one B2 worker before adding the two initial API apps. | Platform-owner cost/change approval and coordinated change window; measured capacity still required. |
| PLATFORM-PROP-02 | Add one shared classic APIM Developer unit and one shared Basic ACR in Australia East. | Platform-owned hosting; Parameter Pilot owns approved APIs/policies/images. No subscription-wide app deployer grant. |
| PLATFORM-PROP-03 | Add two service-isolated Free App Configuration stores and two Standard Key Vaults, all platform-owned, for Aquarium and Tracking. | Architectural refinement requiring approval under ADR-027; see proposed ADR-031. Store lifecycle remains outside application control. |
| PLATFORM-PROP-04 | Establish scoped SQL/identity/data/config/registry grants, and reconcile the four shared diagnostic tables to 30 days after checking other consumers. | Explicit identity/assignment scopes and shared retention approval; no removal of legacy access without a reviewed replacement. |

Design acceptance is distinct from permission to deploy/spend. A later deployment approval must name the reviewed platform revision/what-if, target subscription/environment, allowed operations and budget. This proposal has not been accepted.

## Resource schedule

Target subscription `9671ac36-9800-451a-b283-35ea87f8b419`, resource group `rg-platform-dev`, region Australia East. Names are candidates; check global availability and naming policy before implementation. Do not silently change regions, stores or SKUs on availability failure.

| Resource | Candidate name | Proposed setting |
| --- | --- | --- |
| Existing App Service Plan | asp-platform-dev | Linux B2, capacity 1; retain resource ID and other apps. |
| Shared APIM | apim-adt-platform-dev | Classic Developer, capacity 1, public gateway HTTPS, no initial VNet/Front Door/WAF. Publisher contact supplied by owner. |
| Shared ACR | acradtplatformdev | Basic; admin account and anonymous pull disabled; repository-aware RBAC/ABAC for app isolation. |
| Aquarium App Configuration | appcs-adt-aquarium-dev | Free, local access-key authentication disabled; Aquarium-specific Entra data grants. |
| Tracking App Configuration | appcs-adt-tracking-dev | Free, local access-key authentication disabled; Tracking-specific Entra data grants. |
| Aquarium Key Vault | kv-adt-aquarium-dev | Standard, RBAC enabled, soft delete 90 days, purge protection enabled; protected deletion is intentional. |
| Tracking Key Vault | kv-adt-tracking-dev | Same policy, independent service access. Tracking OBO certificate's secret/private-key access granted only where needed. |

Per-service App Configuration/Key Vault instances are proposed so isolation does not depend on prefixes, labels or complex per-object administration. They are still managed and paid for by the Shared Platform. Explicit shared nonsecret values may be deployed to both stores from one reviewed source; no third shared store is required initially. Each workload keeps its own identity and receives only its required subset of secrets. A store-level reader may read all service nonsecret settings; do not place workload-private secrets there.

Two Free configuration stores fit Microsoft's documented limit of three per region/subscription. Each has a documented 1,000-request daily limit; startup configuration reads, deployment checks and restart frequency must fit that allowance. Dynamic polling is already deferred. Observe quota consumption and fail safely on exhaustion; no automatic paid upgrade. If Free is unavailable or insufficient, a focused change to two Developer stores adds approximately A$10.40/month at the quoted rate. No SLA/production readiness is inferred from Free.

Key Vault access is RBAC-based. Prefer object-scoped Secrets User reads for unavoidable private secret subsets within a service; object creation/rotation rights belong to the controlled service deployment/operator path, not runtime. Neither vault gets general cross-service read grants. Authorise the required data-plane access for certificate private-key retrieval explicitly; a management Reader role alone is insufficient. Public TLS endpoints initially remain subject to Entra access controls; network firewall restrictions must preserve documented developer/CI/workload paths. No private endpoint/NAT/VNet spend is bundled into this proposal.

## APIM ingress and registry feasibility

[Microsoft's address documentation](https://learn.microsoft.com/en-us/azure/api-management/api-management-howto-ip-addresses) distinguishes classic Developer's dedicated addresses from the nondeterministic addresses of Consumption/v2 tiers. Recommend Developer because it matches ADR-026's public HTTPS backend restriction approach without a whole-region allowlist. It is a nonproduction tier. After creation, retrieve the actual APIM address and verify its effective source at the backend. Static addresses can change on documented lifecycle operations; make re-verification part of that runbook.

Future application deployment must apply default-deny App Service rules permitting only the verified APIM and necessary workload address sets, with independent token/scope/ownership checks. Control SCM/deployment/probe paths separately. Prefer image-based management-plane deployments that do not require opening SCM to all GitHub-hosted runners. If narrowly scoped operational access cannot be demonstrated, return for an ingress/deployment design decision. No whole Azure-region/Internet allow rule or forged header exemption is permitted.

Shared ACR must not grant unconditioned registry-wide push/pull access to an application identity. Use repository ABAC conditions for `parameterpilot/aquarium-api` and `parameterpilot/tracking-api`; assign Repository Reader to each respective runtime identity and Repository Writer to the scoped image publisher. No delete right or catalog-list permission by default. [Microsoft documents](https://learn.microsoft.com/en-us/azure/container-registry/container-registry-rbac-abac-repository-permissions) that legacy AcrPull/AcrPush roles are not honoured in ABAC mode; verify actual App Service managed-identity pull compatibility before acceptance. If that path fails, propose a scoped alternative rather than enabling admin credentials or registry-wide reads.

## Capacity recommendation and change safety

The existing B1 plan has four apps, roughly 79% average memory and 93% peak in the inventory window. Adding two APIs is not accepted on that evidence. B2 increases available compute/memory on the existing platform boundary; this is a proposed starting capacity, not proof of performance. Keep one worker and avoid introducing independent app scaling.

Before changing SKU: capture current plan/app configuration and addresses without secrets, owner-designate a change window, record health baselines and notify affected project owners through their approved process. Scale operations may restart/move workloads; do not promise uninterrupted operation. After change, verify all existing apps, addresses and network rules. Do not deploy Parameter Pilot APIs in the same operation.

During authorised API bootstrap, observe process memory, cold starts, CPU and dependency latency for the two new apps alongside existing consumers. Proposed investigation trigger: sustained plan memory above 80% for 15 minutes or a repeatable API health regression; re-evaluate capacity rather than automatically scaling. This trigger is a proposal, not an availability promise or existing alert. Defer workers and commercial load tests. Returning to B1 requires owner approval and proof that current workloads fit; automatic downscale could disrupt all consumers.

## Permissions and existing shared resources

| Principal/path | Proposed permissions | Excluded |
| --- | --- | --- |
| Platform deployment operator | Explicit platform resource management and controlled role-assignment authority needed for the reviewed change | Application pipelines inheriting subscription Contributor/Owner. |
| SQL administration | Owner-designated Entra security group as SQL administrator; retain existing SQL auth temporarily for consumer compatibility | Assuming the executing user should be SQL admin; Entra-only switch or removal of current firewall/login access. |
| Aquarium runtime | Contained SQL user for managed identity, required read/write/execute within Aquarium schema only; corresponding service config and scoped secret reads | db_owner, other schemas, Tracking data, migrations/DDL. |
| Aquarium migration identity | Separately approved Aquarium schema/migration permissions and scoped deployment management | Runtime reusing elevated migration identity. Exact SQL grants reviewed with migration design. |
| Tracking runtime | Cosmos built-in/custom data role restricted to its approved container scope in ReferenceProjects; /tankId, panel/idempotency/outbox local transaction preserved | blastplanning-events, shared throughput management, Aquarium SQL. No account key fallback. |
| Application deployment | Explicit approved child resources in app group, service content/config and repository Writer; OIDC restricted to trusted repo/environment | Generic Contributor on all shared platform resources, cross-project stores/secrets, broad role-assignment authority. |
| Developer | Individual Entra login, approved Development-only data/config access and distinct Local OBO certificate | Shared accounts, copied workload credentials or production access. |

Principal GUIDs, approved Cosmos container name, SQL admin group and exact custom-role actions must be resolved in the implementation parameter/permission manifest. No fictitious principal IDs or speculative assignments are deployable. Test successful required reads/writes, denied other-service/other-project access and denied runtime administration under the actual identities; the operator's Owner access proves none of these.

Retain the shared SQL database, Cosmos database/400 RU/s, Service Bus and existing telemetry resources/SKUs. Do not disable local auth or remove the SQL Azure-services-wide firewall rule as part of this proposal; first inventory existing consumers and prepare a separate safe cutover if required. Do not assume that leaving them unchanged establishes the desired app grants. SQL schema grants need a controlled SQL data-plane task after Entra administration; Bicep alone does not prove schema isolation.

For AppRequests/AppTraces/AppExceptions/AppDependencies, propose table retention and total retention of 30 days, plus aligned component configuration. Confirm other consumers have no required longer retention/legal hold before any reduction. Reducing retention can make older data irrecoverable; export/retain required data or obtain explicit data-loss acceptance first. If shared consumers need 90 days, propose a separate Parameter Pilot telemetry boundary for review instead of silently shortening shared retention. No reduction is authorised now.

## Cost estimate and controls

Source: [saved public retail-price evidence](platform-pricing-2026-10-30.json), fetched from the [Microsoft Retail Prices API](https://prices.azure.com/api/retail/prices) on 30 October, AUD/Australia East/Consumption. Model a 730-hour month and 730/24 days; these are estimates, not an account-specific quote. Exclude tax, credits/Dev-Test discounts, FX changes, egress, telemetry, CI, extra registry storage/build tasks, other resources and usage-dependent operations. Requote before deployment.

| Item | Retail rate | Monthly fixed estimate |
| --- | --- | --- |
| APIM Developer, one unit | A$0.0937/hour | A$68.40 additional |
| ACR Basic, one registry | A$0.2373/day | A$7.22 additional |
| Two App Configuration Free stores | A$0/store/day | A$0 |
| Shared Linux plan B1 -> B2 | B1 A$0.0271/hour; B2 A$0.0527/hour | A$18.69 increase; B2 total A$38.47 |
| Two Standard Key Vaults | Operations A$0.0427/10,000; no fixed-instance charge in this model | Usage-dependent; 100,000 standard operations total would be A$0.43. Certificate issuance/renewal/rotation meters excluded. |
| **Estimated fixed increase** | APIM + ACR + plan delta | **A$94.31/month**, plus variable charges |

The selected items including the full B2 plan total approximately A$114.09/month fixed, of which A$19.78 is the current B1 baseline; this is not the total Shared Platform bill. Keeping B1 avoids A$18.69/month increase but leaves the observed capacity risk unresolved and is not recommended for API deployment. Two App Configuration Developer stores cost A$0.171/store/day, approximately A$10.40/month extra if later approved.

Propose an incremental planning allowance of A$120/month with owner alerts at 50/80/100%, reviewed alongside the actual subscription bill. This allowance and notification destination require owner approval. Budgets notify; they do not impose a spending cap. Do not auto-stop/delete shared services to enforce cost limits. Attribute tagged service resources directly, and track shared B2 delta separately; a native Azure budget cannot directly subtract a prior B1 baseline. No budget/alert or billable resource was created.

## Implementation, verification and approval sequence

1. Obtain decisions on PLATFORM-PROP-01–04, the new isolated-store topology (ADR-031), fixed/variable cost allowance and retention consequences. Obtain owner publisher/alert email, SQL admin group object ID and intended application/deployment identity references; keep secret values outside the review artefacts.
2. Under applicable platform-source authorisation, create a separate task branch in azure-reference-platform. Add reviewed modules/parameters and deployment outputs for proposed resources, scoped assignments and B2 change. Keep app APIs/policies/images/schema/container content in application-owned paths; no application workloads or data migrations in the platform deployment.
3. Update accepted ADR/model/documentation after the topology decision. Build/lint Bicep, validate names/providers/tiers/quotas, check public exposure and deletion/purge policies, and perform a nondeploying what-if with the exact parameter set. Reject unexpected deletes/replacements, other-project changes, throughput increases and unapproved broad grants. No what-if is claimed yet because there is no approved implementation/template for this proposal.
4. Present the exact revision, what-if, permission manifest, plan window and updated estimate for deployment approval. Deploy in coordinated stages: additive stores/registry/APIM; isolated capacity operation; controlled identity grants; separately approved retention reconciliation. Do not combine retention loss with a routine infrastructure update.
5. Verify actual resources/SKUs/addresses, managed-identity reads/pulls and denial cases, existing app health and retention settings; record deployment correlation/revision and owner handover. Actual app-operation tests arrive with the authorised bootstrap/slice. No dummy worker or invented end-to-end evidence.

Recovery: additive unused resources can remain while a failed access/config step is corrected; do not broadly grant access to make tests pass. Do not delete vaults or disable purge protection as rollback. Preserve old app/config values until replacements are verified. Review B2 rollback against current load. Permission rollback targets only assignments introduced by the reviewed operation; never strip unrelated roles. Retention reduction requires explicit prior preservation/acceptance, because a setting rollback cannot restore expired data.

## Architecture impact and review status

Proposed ADR-031 refines ADR-024/027 to platform-managed per-service configuration/vault instances. ADR-026 is retained through classic APIM Developer; ADR-011/024's shared-plan boundary remains, with a proposed B2 capacity change. The authoritative Structurizr workspace, model/systems.dsl, model/relationships.dsl, model/deployment.azure.dsl and views/views.dsl were consulted. Configuration/vault infrastructure is currently omitted from the logical model; any approved representation must be added consistently there rather than recreated independently. Deployment sharedPlan/sharedGateway descriptions may need exact approved settings; no DSL was changed or duplicate C4 diagram created.

Verified for this proposal: published tier/address/quota/ABAC guidance; public AUD rate records and arithmetic; local document links/JSON. Not verified: global name availability, deployable parameter set, quota/region allocation, exact principal grants, Bicep build/what-if, backend addressing, runtime image pull, incremental capacity, effective isolation, account-specific billing or retention consumer acceptance. All PLATFORM-PROP decisions remain Proposed.
