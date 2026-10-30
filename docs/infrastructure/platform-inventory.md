# Shared-platform repository inventory and ownership

Version: 0.3 | Date: 30 October 2026 | Status: Source inventory plus live resource metadata; operational readiness pending

## Current live evidence

Current ownership correction: PP-exclusive App Configuration stores/Key Vaults belong to PP and are deferred until PP Bicep is altered (accepted ADR-031). Historical platform-owned configuration/vault statements below are superseded; actual provisioning and isolation tests remain open. The next [scoped-access task](scoped-access-readiness.md) has a dedicated SQL administrator group selected, but no group/admin/grants applied.

Subsequent [APIM/ACR deployment on 30 October](platform-foundations-draft-2026-10-30.md) succeeded through the existing main.bicep/local parameter path. APIM Developer/policy and ACR Basic now exist and their infrastructure controls were checked; B1 and verified existing settings/app states were retained. App Configuration/Key Vault, scoped access and application ingress/identity/handover remain outstanding. The pre-deployment source/read-only inventory below is historical for the now-provisioned APIM/ACR resources.

The [30 October readiness report](platform-readiness-2026-10-30.md) verifies core deployed resources and records actual IDs/settings, shared-plan load, missing APIM/ACR/configuration/secrets prerequisites, absent SQL Entra administration/Cosmos data-role assignments, and 90-day diagnostic table retention. Resource existence is now verified for the listed core resources; operational access, isolation, capacity acceptance and handover remain open. No Azure or platform-source changes were made. The older source-only statements below describe the 20 October inspection and are superseded by that report for observed live state.

Source: C:\Git\azure-reference-platform. Read-only inspection; no platform source, credentials or deployment state changed.

## Repository evidence

Sources: README.md, docs/resource-ownership.md, docs/deployment-settings.md, docs/cost-model.md, infra/bicep/main.bicep, modules and environments/dev/main.dev.bicepparam. Local override parameter values were not used to establish actual deployment.

| Resource | Development definition | Ownership/use |
| --- | --- | --- |
| Resource group | rg-platform-dev, Australia East | Platform |
| App Service Plan | asp-platform-dev, Linux B1 | Platform capacity; application workloads require verification |
| SQL server/database | sql-adt-platform-dev / ReferenceProjectsDb; Basic, 2 GiB configured | Platform database; accepted Aquarium schema/tables/migrations app-owned |
| Cosmos account/database | cosmos-adt-platform-dev / ReferenceProjects; Session, 400 RU/s database throughput, free-tier configuration | Platform account/database/throughput; Tracking containers app-owned |
| Service Bus | sb-adt-platform-dev, Standard | Platform namespace; application entities/approved access app-owned |
| Monitoring | appi-platform-dev and log-platform-dev, 30-day configured log retention | Shared hosting/policy platform-owned; application telemetry configuration scoped |

These are source defaults, not confirmation of deployment, free-tier entitlement, bill, available headroom, permissions or production suitability. Runtime/OS/Always On, network exposure, identity/data-plane and migration permissions, backup/restore and actual capacity still need verification.

APIM, ACR, Key Vault, App Configuration, Blob Storage and PostgreSQL were not defined in the inspected platform Bicep. Do not assume they exist; target shared ownership is now accepted below, but provision/deployment still requires the owner's separate request.

## Accepted boundaries

Aquarium uses schema Aquarium within shared ReferenceProjectsDb. Tracking owns containers/indexes/data lifecycle within shared ReferenceProjects; history partition is /tankId. App identities may access only the approved schema/containers; no cross-service data access. Outbox/state transactions remain local to the schema/database or one Cosmos container/logical partition.

Platform owns shared capacity/SKUs and platform-wide security/network settings. App pipelines reference existing hosting and manage approved child resources only. Any required broad-scope role assignment or shared resource change requires platform-owner authorisation; text ownership is not an access-control grant.

## Documentation differences

The platform resource-ownership document describes app-owned Cosmos databases, while current main Bicep creates ReferenceProjects. ADR-024 explicitly chooses Tracking-owned containers within that shared database for this app. Historical Orders/Catalog/Payments names in platform documentation are legacy, not Parameter Pilot service boundaries.

## Outstanding evidence

Capture actual resource IDs/locations/SKUs, deployment revision, delegated management permissions, SQL/ Cosmos data-plane roles, capacity usage, monitoring access and restore ownership. Source-level inventory is complete for this decision; live verification remains a Stage 1 readiness item.

## Accepted target extension after initial inspection

The owner agreed platform-managed APIM, ACR, Key Vault, App Configuration, Blob account and PostgreSQL server; app owns corresponding API/image/config/secret/container/database content. Those resources were absent from the earlier inspected Bicep; acceptance is target ownership, not proof of addition/deployment. Owner will separately request platform changes/deployment before Parameter Pilot agentic implementation. Verify resource IDs, isolation, capacity and delegated scopes at handover. Initial cloud scope is Development only (ADR-025).
