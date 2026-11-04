# Aquarium and Tracking foundation review

**Closeout update, 4 November 2026.** Stage 1 is complete and owner-accepted. The deployment notes below preserve the status at the time of each verification. [Stage 1 completion checklist](../engineering/stage-1-completion-checklist.md)

Date: 30 October 2026; layout/naming revised 2 November 2026 | Status: Foundations deployed and management controls verified on 2 November 2026

Authority: the owner requested preparation of PP Bicep changes for review. This authorises source preparation and validation, not deployment, traffic activation, spend, feature implementation or a shared-platform update. Existing Structurizr deployment sources and accepted ADR-009/011/024/026/027/031 were consulted; no new topology or C4 view is introduced.

## Proposed decisions

| Area | Review proposal |
| --- | --- |
| Entry point | Extend existing infra/bicep/environments/dev/main.bicep and environments/dev/main.dev.bicepparam; no independent entry point. |
| Activation | deployServiceFoundations defaults false in both entry point and committed Development parameters. Foundation resources are also gated to dev. Existing website settings/domains are unchanged. |
| Hosting | Two distinct Linux container-host shells on existing asp-platform-dev in rg-platform-dev, Australia East. No plan resource, SKU change, scaling, worker or Advisor resources. |
| Bootstrap state | Apps stopped, no container image or runtime processing, public access disabled, main and SCM default deny, FTP and SCM basic publishing disabled. No APIM route or allowlist added. |
| Identity | One system-assigned managed identity per actual API host. No shared runtime identity or unused worker identity. Outputs provide actual IDs after an approved deployment. |
| Configuration | One Free App Configuration store per service in Australia East, local/key authentication disabled. No configuration content, dynamic refresh or provider fallback introduced. |
| Vault | One Standard RBAC Key Vault per service, soft delete 90 days and purge protection. Purge protection prevents early permanent deletion once enabled; explicitly review before deploying. No secrets, keys, certificates or secret values in outputs. |
| Runtime access | App Configuration Data Reader on own store and Key Vault Secrets User on own vault only. No cross-service access or content administration. Inherited rights still require live review/testing. |
| Store networking | Public authenticated endpoints for configuration/vault data access; vault network bypass None. These are not private endpoints. Entra authorisation enforces content access; API public ingress remains disabled. |
| Naming | Explicit values in main.dev.bicepparam: api-adt-aquarium-dev / api-adt-tracking-dev; appcs-adt-aquarium-dev / appcs-adt-tracking-dev; kv-adt-aquarium-dev / kv-adt-tracking-dev. The deployed resource group and Static Web App names remain unchanged. Global availability must be verified before deployment. |
| Publishing | Add validation-only GitHub Actions workflow: Bicep compilation plus security-boundary checks; no Azure login/deployment. Legacy Azure DevOps pipelines remain trigger/pr disabled; controlled retirement and deployment OIDC remain later delivery work. |

## Verified platform inputs

Read-only Azure metadata confirms the shared plan is Linux/reserved, B1, Australia East. APIM Developer is Succeeded and currently reports outbound IP 4.254.91.56. That observation does not establish a durable complete ingress allowlist. The draft deliberately leaves API ingress disabled; API/workload/SCM/probe routes need separate feasibility and effective-access testing before activation.

No App Configuration stores were returned for the subscription. Microsoft's current documented Free limit is three per region per subscription, so two initial stores fit the observed inventory. Recheck availability and provider quotas at deployment; do not upgrade tiers automatically. Free requests are limited and shared B1 capacity is not proven by stopped hosts. No new fixed compute plan is proposed; vault operation, logging and network usage remain variable under the accepted portfolio budget.

Sources: [App Configuration limits](https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/azure-subscription-service-limits#azure-app-configuration), [configuration RBAC](https://learn.microsoft.com/en-us/azure/azure-app-configuration/concept-enable-rbac), [vault RBAC](https://learn.microsoft.com/en-us/azure/key-vault/general/rbac-guide), [App Service restrictions](https://learn.microsoft.com/en-us/azure/app-service/app-service-ip-restrictions).

## Review and validation

Compile through the established path:

```powershell
az bicep build --file infra/bicep/environments/dev/main.bicep --outfile "$env:TEMP/pp-main-review.json"
az bicep build-params --file infra/bicep/environments/dev/main.dev.bicepparam --outfile "$env:TEMP/pp-dev-review.json"
python scripts/verify-service-foundations.py "$env:TEMP/pp-main-review.json" "$env:TEMP/pp-dev-review.json"
```

Review an opt-in preview without changing the committed safety switch:

```powershell
az deployment sub what-if --location australiaeast --template-file infra/bicep/environments/dev/main.bicep --parameters infra/bicep/environments/dev/main.dev.bicepparam --parameters deployServiceFoundations=true
```

Local Bicep and committed parameters compile successfully. The compiled-template verifier checks stopped/closed hosts, existing-plan reference, service isolation, exact resource types and read-only grant roles, low-cost SKUs, deletion protections and absence of credential retrieval. Seven deliberate unsafe mutations were rejected: starting/opening apps, opening SCM, enabling store keys, raising store SKU, disabling vault RBAC and broadening a grant to resource-group scope. These are static safeguards, not live access tests.

## Azure preview result

The 30 October full main.bicep opt-in what-if succeeded with no diagnostics or skipped modules. It proposes 14 creations: two hosts, four publishing-credential policy children, two configuration stores, two vaults and four store/vault role assignments. No deletions or shared-platform mutations were returned. The shared plan ID is explicitly subscription/resource-group qualified; the earlier incomplete nested preview was corrected and superseded.

Three existing-resource Modify entries remain on the website and two domain bindings. Website delta paths are deploymentAuthPolicy, provider, stableInboundIP, trafficSplitting and buildProperties; domain deltas are expiresOn, isDefault and validationMethod. These arise from the existing website module/provider representation, which this draft leaves unchanged. They are not automatically approved or proven harmless. Before deployment, resolve/preserve the live settings or obtain explicit review of the complete deltas. Do not treat the child-module preview as a replacement deployment path.

The [30 October review evidence](evidence/pp-service-foundations-review-2026-10-30.json) is historical and uses superseded draft names and source hashes; it does not validate the 2 November refactor. Current layout, naming and validation are recorded in [the infrastructure guide](../../infra/README.md). A successful what-if is not proof of name availability, role propagation, future image startup, capacity or effective data-plane isolation.

## Deployment and follow-on gates

Before any deployment: owner reviews this proposal and actual preview, global names/provider availability, vault deletion protection, public authenticated store endpoints and scoped role assignments. Confirm the deploying identity can create PP resources and role assignments and join the existing shared plan without granting runtime platform management rights. No new subscription-wide or cross-product grant is proposed.

After an approved foundation deployment: verify output principals, allowed own-store/vault reads, denied cross-service/admin writes and preserved other-product settings. Configure actual scoped Aquarium users and migration grants only after schema/object decisions are concrete. Tracking container/name/indexes and Cosmos role grants remain a separate PP-owned shared-database slice; no container or throughput change is in this proposal. Container images, repository-scoped ACR grants, API token/owner validation, APIM routes, narrow ingress, ordinary developer rights and deployment OIDC must be reviewed and tested before starting APIs.

This draft does not complete Stage 1 scoped access. It creates no Azure resource during preparation and contains no feature implementation or workload credentials. It has not been committed, pushed or run on GitHub as part of this preparation.

## Resource-type organisation — 2 November 2026

The owner requested full alignment with BlastIQ Bicep organisation and comment style. The environment main now wires appservice.bicep, app-config.bicep, key-vault.bicep and role-assignments.bicep directly; the service-foundation bundles were removed. Static Web Apps retain their resource-specific module. Names, security settings and the disabled opt-in remain unchanged. The parameter file and entry point use the reference project’s banner sections; the generated main.json and compiled-boundary verifier are updated. See the [module guide](../../infra/README.md#resource-type-modules-and-shared-formatting). This authorises no deployment or new permissions.

## Authorised deployment preview — 2 November 2026

The owner authorised deployment-preparation item 1 only. The final resource-type module structure compiled, all seven static unsafe-mutation checks passed, and the full subscription what-if succeeded with no diagnostics or skipped resources. deployServiceFoundations=true was supplied as a preview override only; the saved Development file remains false. No deployment was performed.

The preview reports 14 Create, three Modify and one NoChange entries. Creations are two API hosts, two configuration stores, two vaults, four basic-publishing-policy children and four scoped read-role assignments. All changes are within rg-parameterpilot-dev; no deletion or shared-platform mutation is proposed. The previewed API hosts remain disabled with public access disabled.

The three Modify entries are the existing Static Web App and its two custom-domain bindings. Website differences cover deploymentAuthPolicy, provider, stableInboundIP, trafficSplitting and buildProperties. Domain differences cover expiresOn, isDefault and validationMethod. Some returned fields may be provider metadata; this preview does not prove those differences harmless or approve their application. Item 2 must resolve/preserve existing website/domain behaviour before deployment.

[Current preview evidence](evidence/pp-deployment-preview-2026-11-02.json) records source hashes, safe resource IDs and complete delta details. This supersedes earlier previews for the current resource-type module layout and explicit names. Name availability, quotas, deployment authority and effective data-plane access remain separate checks.

## Authorised deployment outcome — 2 November 2026

The owner subsequently authorised deployment and accepted possible coming-soon website disruption from the reviewed website/domain differences. See [the authorisation record](../engineering/authorised-decisions-2026-11-02.md). Earlier review-only statements describe the preparation stage; they no longer mean the foundations are undeployed.

Deployment `pp-foundations-dev-20261102-1e43f0ac` Succeeded in approximately 82 seconds. The refreshed preview matched the accepted 14 creations and three existing website/domain modifications, without deletion or shared-platform mutation. The deployServiceFoundations=true override was applied for this run; the saved parameter remains false. Future full-foundation deployments must explicitly enable that parameter; false skips management of those resources under incremental deployment and does not delete them.

Both API hosts have distinct system-assigned identities, enabled=false and publicNetworkAccess=Disabled. Main/SCM deny defaults, HTTPS/TLS controls and disabled basic publishing were verified. Both configuration stores are Free with key authentication disabled; both vaults are Standard with RBAC, 90-day soft delete and purge protection. Management-plane role inspection found exactly two intended store/vault read grants per identity, no cross-service/admin grant. This is not proof of effective workload data-plane access.

The shared Linux B1 SKU and all three pre-existing applications on the plan matched their before-deployment snapshots. The default website and parameterpilot.com/www.parameterpilot.com returned HTTPS 200 with certificate validation. No apparent website disruption was observed.

[Deployment evidence](evidence/pp-foundations-deployment-2026-11-02.json) records actual principal/resource IDs, source hashes, deployment details and verification limits. No secret values or customer records were read. Application images/activation, APIM routing/ingress, effective configuration/vault read/denial tests, SQL/Cosmos schema/container/user/grants and ordinary developer/deployment permissions remain follow-on work. Stage 1 scoped access is not complete.
