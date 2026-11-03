# Step 3 permission matrix — for owner review

Date: 3 November 2026. Historical review proposal: the owner subsequently authorised implementation. Applied identities, environments, grants and verification limits are recorded in the [delivery access runbook](delivery-access.md). The observations/proposals below preserve the review baseline; they are not the current deployment inventory.

## Observed state

- The signed-in owner has subscription Owner and shared SQL administrator membership. These privileges cannot prove ordinary developer isolation and will not be removed as part of PP setup.
- The shared-platform GitHub principal `github-azure-reference-platform` (`178b93a5-0613-4665-9584-c82c073f4885`) and two `ausdatatech-Public Portfolio-*` principals (`bbac4be8-0d2a-4ae4-8525-3c4f008e40ae`, `0ab80c14-53a9-4011-b832-a51abfa8e42c`) inherit subscription Contributor. The latter two have not been mapped to their actual legacy service connections. Do not reuse or remove them without confirming ownership and coordinating the step 7 cutover.
- Targeted Entra name searches found no dedicated PP deployment/migration application or developer group. No user-assigned identity exists in the PP resource group. This is not an exhaustive directory audit.
- GitHub `PhilipTodd/azure-distributed-systems-reference` is public, with default branch `main`. Repository secret and variable name lists are empty. The only environment returned is `github-pages`, with a branch policy and no environment secrets/variables; there is no Azure `dev` or migration environment. No secret values were retrieved.
- The two actual API system identities and their service-specific configuration/vault permissions are verified in steps 1 and 2. `AquariumMigrations` exists with CREATE object rights and ALTER on Aquarium only, but no member. Neither domain tables nor migration history exists yet.

## Proposed identities and permissions

All names below are proposals, not deployed resources. Use existing shared services; no new paid hosting tier is proposed.

| Principal | Proposed access | Exclusions and limits |
| --- | --- | --- |
| `github-parameterpilot-deploy-dev` | GitHub OIDC; publish to ACR repositories `parameterpilot/aquarium-api` and `parameterpilot/tracking-api` with repository-conditioned Repository Writer. Custom app-release permissions on the two existing API hosts for configuration/container updates and restart. Website deployment permission scoped to the existing Static Web App. | No subscription/RG Contributor, IAM writes, SQL/Cosmos grants or Key Vault secret-value grants. Exact custom role actions and Static Web App deployment-token method must be previewed before application. This role does not authorise the full infrastructure main.bicep deployment. |
| `github-parameterpilot-migrations-dev` | Separate protected GitHub OIDC environment; contained SQL user mapped to verified application/client ID; CONNECT and membership in `AquariumMigrations` only. | No db_owner, user/role administration, shared SQL firewall writes, other-product schemas, registry publication or vault access. Additional migration DML/history permissions must be explicit and reviewed; existing ALTER/CREATE alone is not a complete migration grant. |
| `sg-adt-parameterpilot-developers-dev` | Philip initially; Reader on PP RG, Data Reader on the two PP configuration stores. Container-scoped Cosmos read/query/feed access to `parameterpilot-tracking`. SQL CONNECT and SELECT on explicitly approved Aquarium objects when they exist. | No production-wide database reader/writer, DDL, migration history writes, Key Vault secret-value access, registry push or cross-product data access. Start with cloud read-only access; use Local dependencies for ordinary development writes. Philip's inherited administration still applies. |
| Aquarium / Tracking API identities | Repository Reader conditioned to each service's own proposed image repository, alongside the already verified service-specific data/configuration/vault permissions. | No registry catalog listing, cross-repository pull or publication. Preserve existing runtime isolation. |
| Existing owner/bootstrap session | Controlled, explicitly authorised infrastructure deployment, directory/group setup, SQL security bootstrap and role assignment. | Keep privileged infrastructure maintenance separate from routine application releases. Do not copy Owner/User Access Administrator to automation. |

An app-release identity can deploy code that uses the host's runtime identity; it must therefore be treated as trusted for that service's runtime data. Absence of direct data-plane grants does not remove this indirect authority. Vault/store resource writes can also change access settings; exclude them from the routine app-release role.

## GitHub trust proposal

Use issuer `https://token.actions.githubusercontent.com` and audience `api://AzureADTokenExchange`, with these separate subjects:

- `repo:PhilipTodd/azure-distributed-systems-reference:environment:dev`
- `repo:PhilipTodd/azure-distributed-systems-reference:environment:dev-migrations`

Create those environments with main-only deployment branch policies and owner approval. Allow the owner to approve their own deployment run so this single-developer project remains usable. Environment-based subjects alone do not constrain the branch: the environment policy and workflow branch guard are required. Grant `id-token: write` only to the relevant job. Store tenant, subscription and separate client IDs as nonsecret environment variables; do not create client secrets. Workflow implementation, successful deployment runs and legacy cutover remain step 7.

## Migration and runtime grant process

Keep Aquarium schema ownership distinct from dbo. For Stage 1, verify migration CREATE/ALTER on disposable Aquarium objects and denied other-schema/security administration, then remove probe objects. Review explicit Aquarium-only DML needed for migration backfills/history before granting it to the migration role. Never extend those schema-wide rights to runtime.

Each Stage 2 migration must include an object permission manifest: exact runtime tables/views/procedures, required operations, and migration metadata excluded from runtime writes. Apply the runtime grant manifest through the controlled security bootstrap; the migration principal receives no general GRANT authority. Verify both positive runtime operations and denied migration-history/other-product access after each change. Do not invent domain tables to close Stage 1.

## Verification and remaining decisions

Owner review is needed for the proposed identity/group/repository names, read-only cloud developer baseline, separate deployment/migration environments and owner-controlled infrastructure/security bootstrap. Before grants are applied, prepare the exact role definitions, ABAC conditions, SQL statements and changes to reproducible scripts/Bicep for review.

Effective developer denial tests require a separately scoped verification principal, not Philip's administrator session. Propose a temporary user-assigned verification identity with the same approved access profile, attached to a closed verification host and removed afterwards; this requires explicit authorisation. Migration and registry tests must also use the actual effective identities, demonstrate cross-product/admin denial and remove synthetic artifacts. GitHub environment enforcement must be checked by execution in step 7; inventory alone does not prove it.

No changes to service/store boundaries or authoritative C4 views are proposed. Existing Structurizr source was consulted; this document specifies operational access preparation rather than a replacement architecture model.

References: [GitHub Azure OIDC](https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-in-azure), [ACR repository ABAC](https://learn.microsoft.com/en-us/azure/container-registry/container-registry-rbac-abac-repository-permissions), [authoritative Stage 1 checklist](../engineering/stage-1-completion-checklist.md).
