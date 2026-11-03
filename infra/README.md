# Parameter Pilot infrastructure

The folder layout follows the BlastIQ mining-event-sourcing-reference application. Resource values are supplied explicitly by the environment parameter file; modules stay reusable. The organisation was prepared as a source refactor; the owner subsequently authorised the Development foundation deployment on 2 November 2026.

```text
infra/
  bicep/
    environments/
      dev/
        main.bicep
        main.dev.bicepparam
        main.json
    modules/
      cosmos-container.bicep
      static-web-app.bicep
      appservice.bicep
      app-config.bicep
      key-vault.bicep
      role-assignments.bicep
      deployment-role-definitions.bicep
      deployment-access.bicep
      registry-access.bicep
      developer-cosmos-access.bicep
  pipelines/
    deploy-infra-dev.yml
    deploy-ui-dev.yml
  sql/
    001-bootstrap-aquarium-access.sql
```

The Development entry point is bicep/environments/dev/main.bicep. main.json is its regenerated compiled template, matching BlastIQ's colocated artifact convention. Shared modules use ../../modules paths. The existing ignored local override was renamed to main.dev.local.bicepparam; its template reference and renamed parameter keys were updated while preserving private values. It remains ignored and is not included in evidence or source hashes. No SQL scripts or application-build pipelines are invented before their implementation exists.

Legacy Azure DevOps definitions are renamed to match BlastIQ's deploy-infra-dev / deploy-ui-dev convention. Both retain trigger: none and pr: none. Any externally configured Azure DevOps definition referring to an old YAML path must be updated manually during the authorised delivery cutover. The GitHub validation workflow references the new Bicep paths and performs no deployment.

## Development resource names

| Resource | Explicit name | State |
| --- | --- | --- |
| PP resource group | rg-parameterpilot-dev | Existing; preserved |
| Static Web App | stapp-adt-parameterpilot-dev | Existing; preserved |
| Aquarium API | api-adt-aquarium-dev | Deployed; disabled and ingress blocked |
| Tracking API | api-adt-tracking-dev | Deployed; disabled and ingress blocked |
| Aquarium App Configuration | appcs-adt-aquarium-dev | Deployed; Free |
| Tracking App Configuration | appcs-adt-tracking-dev | Deployed; Free |
| Aquarium Key Vault | kv-adt-aquarium-dev | Deployed; Standard |
| Tracking Key Vault | kv-adt-tracking-dev | Deployed; Standard |
| Existing shared platform resource group | rg-platform-dev | Referenced scope only |
| Existing shared Linux App Service Plan | asp-platform-dev | Existing reference; no plan mutation |

Static Web App domain children are parameterpilot.com and www.parameterpilot.com. Each API has basicPublishingCredentialsPolicies/ftp and basicPublishingCredentialsPolicies/scm children. The four store/vault read-role assignments use deterministic guid(store-or-vault resource ID, corresponding API resource ID, role definition ID), scoped to that individual service's resource. System-assigned identities have no independently named identity resource.

Nested deployment names are parameterpilot-static-web-app-dev and parameterpilot-{aquarium|tracking}-{app-config|key-vault|appservice|runtime-access}-dev. They are deployment records, not additional hosting resources.

The source refactor changes only undeployed draft API/store/vault names, not the deployed website or resource group. No shared database, SQL schema, Cosmos container, worker, registry or messaging resource is declared in this PP slice. The foundation switch remains false in the committed Development parameters.

## Validation

```powershell
az bicep build --file infra/bicep/environments/dev/main.bicep --outfile infra/bicep/environments/dev/main.json
az bicep build-params --file infra/bicep/environments/dev/main.dev.bicepparam --outfile "$env:TEMP/pp-parameters.json"
python scripts/verify-service-foundations.py infra/bicep/environments/dev/main.json "$env:TEMP/pp-parameters.json"
```

Both builds and the compiled-template boundary checks pass, including seven unsafe mutations. The earlier 30 October Azure preview is historical: its names and hashes do not validate this refactor. No Azure deployment or effective runtime-access test has been performed. Name availability, actual permissions, provider quotas, capacity and the existing website/domain preview deltas remain pre-deployment review gates. See [foundation review](../docs/infrastructure/pp-service-foundations-review.md).

## Resource-type modules and shared formatting

The environment main.bicep wires each resource-type module directly, following BlastIQ's explicit environment orchestration. The old service-foundation.bicep and service-foundations.bicep bundles were removed.

| Module | Responsibility |
| --- | --- |
| appservice.bicep | API host, its system identity and FTP/SCM publishing policies |
| app-config.bicep | Free App Configuration store only |
| key-vault.bicep | Standard RBAC Key Vault only |
| role-assignments.bicep | Own-store/vault runtime read assignments; existing-resource references only |
| static-web-app.bicep | Existing website and custom-domain children |

main.bicep uses the same Deployment, Shared platform resources, Application compute, resource-specific and Outputs banner style as BlastIQ. main.dev.bicepparam follows its Environment, Resource Groups, Locations, Shared Platform Resources, Application Resources and resource-specific section layout. PP-only Deployment Controls retain the disabled foundation switch; no BlastIQ-only storage, messaging, connection strings or workers are copied.

The App Service module receives its own store/vault endpoints; the role module receives the matching App Service principal. This separates resource creation from access grants without a dependency cycle. Names, tags, SKUs, disabled hosts/ingress, vault protection and assignment GUID formulas are preserved. Only nested deployment-record names change to reflect resource-type modules.

Bicep formatting, compilation, committed parameters, seven unsafe-mutation checks and the existing readiness contract checks passed. A pre/post compiled-payload comparison confirmed all seven per-service resource definitions have the same settings after normalising the equivalent module input references. Parameter names/types/defaults/constraints and website resources also match. See [current local evidence](../docs/infrastructure/evidence/pp-resource-type-modules-2026-11-02.json). No Azure deployment or updated Azure preview was performed for this structural refactor.

## Deployment status — 2 November 2026

The owner authorised deployment, including the reviewed existing website/domain deltas. Deployment `pp-foundations-dev-20261102-1e43f0ac` succeeded. The six foundation resources and four scoped read-role assignments now exist; both API hosts remain disabled with public access disabled. The website and domains returned HTTPS 200; shared B1 and existing apps were preserved. Earlier Draft/not-deployed descriptions above are historical preparation notes. Effective workload data-plane isolation, SQL/Cosmos access, images and activation remain pending.

The deployment used an explicit deployServiceFoundations=true override; the saved Development value remains false. Supply that override when managing the foundations through main.bicep again. Under incremental deployment, leaving it false skips those resources rather than deleting them. See [deployment evidence](../docs/infrastructure/evidence/pp-foundations-deployment-2026-11-02.json) and [authorisation](../docs/engineering/authorised-decisions-2026-11-02.md).

## Scoped data access — 2 November 2026

Resource-type module cosmos-container.bicep now owns the approved Tracking container/custom data role/assignment on the existing shared account/database. Existing entry-point parameters gate this with deployTrackingDataAccess (saved false). SQL security bootstrap is in sql/001-bootstrap-aquarium-access.sql, invoked by scripts/bootstrap-aquarium-access.py; no feature tables are created. See [scoped-data-access runbook](../docs/infrastructure/scoped-data-access.md) for actual deployments, validation and limits. This supersedes the earlier statement that this slice declares no Cosmos container or SQL schema.
## Controlled Development delivery access

Step 3 delivery/developer permissions use the existing `bicep/environments/dev/main.bicep` entry point and resource-specific modules. `deployDeliveryAccess` remains false in saved parameters; verified Entra principal/group IDs are explicit deployment inputs. `deployStaticWebApp=false` excludes website/domain maintenance during an access-only deployment. Directory/GitHub bootstrap and SQL setup are separate controlled operations; see [delivery access](../docs/infrastructure/delivery-access.md). No shared-platform password parameter is used.
