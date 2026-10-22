# Azure deployment and ownership

Version: 0.6 | Date: 20 October 2026 | Status: Proposed

Australia East is the accepted preference, subject to actual service/model availability. Budget remains unset; choose appropriate low-cost tiers. No SKU or provisioning approval is established.

| Resource | Purpose | Ownership proposal |
| --- | --- | --- |
| Static Web Apps | Angular assets | Application |
| Front Door/WAF | Deferred until release preparation | No initial dev provisioning |
| APIM | Shared gateway | Platform instance/tier/network/global policy; app APIs/routes/scoped policies |
| App Service | Separate containerised APIs on existing shared Linux plan | App apps/identities/configuration; platform compute/SKU; verify capacity |
| Functions/worker hosting | Three service-owned Function Apps on existing shared-platform App Service Plan, subject to verification | Application apps/identities; platform owns plan/capacity |
| Azure SQL | Aquarium schema inside ReferenceProjectsDb | Platform server/database/capacity; app schema/tables/migrations |
| PostgreSQL Flexible Server / pgvector | Advisor relational state, snapshots and curated retrieval | Platform server/capacity/extensions/backups; Advisor database/tables/migrations/data |
| Cosmos | Tracking-owned containers in ReferenceProjects | Platform account/database/throughput; app containers/indexes/lifecycle |
| Service Bus | One namespace, separate service command queues and event topics/filtered subscriptions | App entities on shared namespace; verify tier/features/isolation |
| Blob | Private photos | Platform storage account; app private containers/originals/derivatives/lifecycle |
| Foundry | Inference | Project/platform allocation TBD |
| ACR | Images | Shared registry with scoped access |
| App Configuration/Key Vault | Config/secrets | Platform development hosting/security settings; app scoped configuration/secrets; enforce isolation |
| App Insights/Log Analytics | Telemetry | Approved isolation/workspace |

## Environments

Accepted ADR-025: initially Local and Development (dev) only. Local uses compatible emulators/test doubles and approved dev dependencies; dev hosts integration tests/demonstrations using synthetic data. Defer Test and Production provisioning until release preparation. Automated testing is required from the start. Production identities/data must be separate; final release topology/security remains to be designed. See [environment specification](../development/environments.md).

## Required platform inventory

Capture IDs, regions, tiers/capacity, network rules, deployment/data-plane roles, backup settings, owner/support and cost allocation. `existing` declarations neither grant permission nor prove isolation. Shared SKUs are changed only by their authorised owner.

Cost scenarios include fixed hosting, data capacity, messaging, storage, PostgreSQL/vector workloads, edge, telemetry and AI usage. Budget alerts need response actions and do not alone stop spend. Budget is not set; estimate costs, document tier tradeoffs and obtain applicable spending/deployment approval. Exposure, retention and recovery still need acceptance.

## Accepted shared-plan worker hosting — 20 October 2026

Target existing shared App Service Plan for Aquarium/Tracking/Advisor Function Apps. Verify OS/SKU/runtime/Always On, permissions and spare CPU/memory/connections before deployment. Shared-plan placement provides independent deployments/identities, not independent compute scaling. Bound image/AI concurrency, monitor contention/backlogs and define extraction criteria before increasing load. No shared tier change or spend is authorised. See [async design](../architecture/asynchronous-processing.md).

## Accepted platform ownership and placement

Source-level inventory is in [platform inventory](platform-inventory.md). Platform owns shared hosting/SKUs/databases/namespace and policy; app owns approved schema/containers/entities and scoped identities/configuration. ReferenceProjectsDb.Aquarium and ReferenceProjects Tracking containers are accepted under ADR-024; /tankId under ADR-005. Existing Bicep definitions do not prove current resource availability, capacity, permissions or deployment. Do not provision separate Aquarium SQL or Tracking Cosmos databases.

## Externally managed shared-platform prerequisite

Owner separately requests platform Bicep additions/deployment before Parameter Pilot agentic implementation. Intended shared APIM/ACR/Key Vault/App Configuration/Blob account/PostgreSQL server supplement the existing platform; they are not yet verified. App agents reference hosting/manage approved children only. This pack neither deploys nor authorises platform changes. Shared Key Vault/configuration must enforce isolation; labels/prefixes alone are not permissions.

## Accepted Development ingress/configuration

ADR-011 accepts separate APIs plus workers on the shared plan. ADR-026 accepts browser traffic through APIM with restricted public backends, conditional on narrow reliable source addressing; no broad-region fallback, independent API authorisation remains. Front Door/WAF deferred. ADR-027 accepts App Configuration/nonsecret flags, Key Vault/secrets, managed identities and untracked local secrets. See [dev access](development-api-access.md) and [configuration](configuration-and-secrets.md); detailed policies remain TBD.
