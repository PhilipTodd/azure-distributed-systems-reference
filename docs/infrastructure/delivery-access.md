# Development delivery and developer access

Date: 3 November 2026. The owner authorised Stage 1 Step 3 after reviewing the permission matrix and discussing where the identities/SQL role reside and how migrations will run. This is Development access setup, not a working product release pipeline.

## Applied setup

| Object | Location / access |
| --- | --- |
| `github-parameterpilot-deploy-dev` | Entra app/service principal; client `1680b16a-c50a-4691-8c84-e681cfb18813`, principal `a733f073-b3b6-45ca-bb28-59f2c6b4c886`. |
| `github-parameterpilot-migrations-dev` | Entra app/service principal; client `83029544-189c-4630-9b9b-d4a23fb3312b`, principal `396641a1-4a8f-4079-ad6c-eef3aba4a9e0`. Contained SQL user is a member of `AquariumMigrations`. |
| `sg-adt-parameterpilot-developers-dev` | Entra security group `ae83484d-7648-4b56-8145-b8fff438a61c`; Philip initially owns/is its sole member. PP RG Reader, both PP configuration stores Data Reader, read/query/feed on the one Tracking Cosmos container. SQL contained group user, CONNECT and `AquariumDeveloper`. |
| `Parameter Pilot API Release Dev` | Custom role assigned only at the two existing API hosts. sites/read, sites/config/read, sites/config/write, sites/restart/action. No sites/write, IAM write, settings-list action or vault/store administration. Configuration writes are still trusted operations and can alter host behaviour. |
| `Parameter Pilot Website Release Dev` | Custom role at `stapp-adt-parameterpilot-dev` only: staticSites/read and staticSites/listsecrets/action. The deployment token can publish website content; never log or persist it. No token was retrieved during setup. |
| Registry release/runtime grants | Shared ACR ABAC Repository Writer for release identity, conditioned to `parameterpilot/aquarium-api` and `parameterpilot/tracking-api`. Each API has Repository Reader conditioned to its own repository. No catalog listing or image deletion grant. Granting access does not create a populated image repository. |
| GitHub environments | `dev` and `dev-migrations`, each main-branch-only, owner approval required, self-approval allowed and admin bypass disabled. Nonsecret variables: AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_SUBSCRIPTION_ID. |

Each application has exactly one GitHub environment federated trust, audience `api://AzureADTokenExchange`, issuer `https://token.actions.githubusercontent.com`, subject `repo:PhilipTodd/azure-distributed-systems-reference:environment:<environment>`. No client secret/certificate credentials were created. These deployment identities are distinct from product user registrations/OBO certificates in Step 4.

The release identity receives no SQL/Cosmos/configuration-value/vault-value roles directly, but deploying API code inherently permits use of that API's runtime access. Treat deployment approval as permission to run trusted code with service data access. Azure RBAC cannot limit sites/config/write to the container-image field: the same action can change authentication/IP restriction settings. The main site's publicNetworkAccess property requires sites/write, which this role does not grant; retain reviewed configuration/ingress checks in the release workflow when Step 5 enables backend traffic.

## Reproducibility and deployment boundary

`scripts/bootstrap-delivery-access.py` defaults to a local plan. Its explicitly applied phases are directory, github, federation, in that order. Directory setup records verified IDs and group membership; GitHub setup verifies protections before the federation phase creates trust. GitHub mode uses `git credential fill`, which must be announced to the owner before execution. Existing ambiguous objects, foreign credentials or unexpected environment policies stop setup for reconciliation. These phases contain no SQL password operations.

Azure role definitions/assignments live in the existing `infra/bicep/environments/dev/main.bicep` path, with resource-specific modules. Saved `main.dev.bicepparam` keeps `deployDeliveryAccess=false` and principal IDs empty. For an authorised access-only deployment:

1. Compile main and its normal Development parameters to temporary JSON.
2. Run `python scripts/bootstrap-delivery-access.py --parameters-output <temporary-parameters.json>` to combine the saved Development values with the verified directory IDs. This local operation sets deployDeliveryAccess=true and deployStaticWebApp=false, leaving deployServiceFoundations=false and deployTrackingDataAccess=false. It reads no local secret parameter file and makes no Azure change.
3. Run subscription what-if through main.bicep/main.json. Reject unapproved changes, modifications or deletions. This deployment preview contained 13 permission additions, with no modification/deletion after excluding the website module.
4. Apply through main. Never deploy the shared-platform main or touch its local SQL-password parameter for this operation.
5. Read back each permission and compare with the preview using `scripts/verify-delivery-deployment.py <preview.json>`.

Deployment `pp-delivery-access-dev-20261103` succeeded; 13 permission resources matched the preview. No unexpected Azure assignments were found for the two new identities/group. Definitions are assignable within the PP RG; actual release assignments are at individual hosts/site. Registry and Cosmos additions reference existing shared resources without changing their capacity/configuration.

The release identity cannot execute the complete infrastructure main deployment. Infrastructure/security maintenance remains owner-controlled. API initial activation, ingress and hosting are Step 5. GitHub release/migration workflows, workflow branch guards, actual OIDC runs, concurrency controls and legacy pipeline cutover are Step 7. No new workflow that deploys to Azure was introduced by Step 3.

## SQL migrations and object grants

`scripts/bootstrap-delivery-sql.py` previews security setup and checks inside a rolled-back transaction by default; --apply commits only approved security objects after successful checks. The migration contained user's SID is the application's client ID (type E); the developer group's SID is its group object ID (type X). Owner-held short-lived Entra SQL tokens are used, never SQL administrator passwords.

Migration role: existing CREATE TABLE/VIEW/PROCEDURE/FUNCTION/TYPE and ALTER Aquarium schema. It has no members other than the new migration user. There are no application tables/history yet. Backfill/history DML required by a real EF migration must be reviewed and granted explicitly before running that migration. Do not assume CREATE/ALTER is a full operational EF grant. Keep Aquarium owned by the isolated AquariumSchemaOwner role.

`infra/sql/runtime-grants.dev.json` is an empty Stage 1 object manifest. Stage 2 migrations must update it with exact objects, types, runtime operations and optional developer SELECT; EF history must live in Aquarium and remain excluded from runtime/developer grants. `scripts/apply-aquarium-object-grants.py` validates/prints by default; --apply uses the controlled owner bootstrap to grant only the reviewed existing Aquarium objects. It rejects schema changes, SQL injection, history access, wildcards, grant authority and developer writes. It grants no general permission-management rights to migration automation. Removed manifest entries do not automatically revoke existing permissions: review explicit REVOKE statements with the relevant migration and verify the resulting effective rights.

Run the schema migration first, apply any approved runtime permission manifest through the controlled bootstrap, verify required runtime access and history/cross-product denials, then release the compatible application. This explicit privilege boundary means a new-table migration may require an owner bootstrap step between migration and app release. Destructive migrations need separate authorisation and a reviewed recovery plan.

## Verification and limits

- Bicep compilation, saved-parameter compilation and foundation/data/delivery boundary checks passed. Delivery checks reject four unsafe mutations (IAM escalation, missing ABAC condition, Cosmos write, enabled saved switch).
- SQL checks passed 20 conditions under the migration contained user and a disposable WITHOUT LOGIN developer-role user. Group principals cannot be impersonated. All test objects/grants rolled back; only the two intended contained principals, memberships/CONNECT and developer role persisted.
- Twelve manifest tests exercise allowed object grants and deny injection, other-schema/history/admin/wildcard/developer-write cases.
- The actual temporary developer-profile identity passed 26 checks: real SQL login/approved SELECT; denied SQL DML/DDL/history/cross-product/admin; both configuration reads and denied writes; both vault secret reads denied; Tracking Cosmos point-read/query allowed and create/other-product access denied; PP metadata read and host administration denied. Run `3c65c56366b3` cleaned its synthetic objects, temporary SQL user, direct Azure/Cosmos grants and identity; original host identity/container/settings and both registry read conditions were restored. This proves the profile, not the developer group's SQL authentication.
- Four read-only checks under Philip's token confirmed both configuration stores and Tracking Cosmos point-read/query access, with the new developer group present in the actual tokens' group claims. These data reads do not prove ordinary-user SQL/ARM restrictions because Philip retains administration.
- Ten registry-token checks passed under the two actual API system identities (five each, including identity verification). Each received own-repository pull authorisation and no other-service/unapproved-repository pull or push action. These are ACR-issued token permissions, not product image deployments. Run `55d2c9e3905f` restored both hosts and original registry conditions, removed its temporary publisher assignment and SQL probe objects/grants. Independent final-state checks confirmed no temporary identity/SQL principal/object remained and exact permanent SQL role membership.
- Live managed-identity verification results and cleanup are recorded separately when available; do not confuse resource read-back or SQL impersonation with authentication by the GitHub principals or the developer group.
- Philip still has inherited subscription Owner/shared SQL administrator access. Group membership does not restrict those rights. No Owner/administrator membership, shared-platform deployment identity or legacy service principal was changed.

The first developer probe could not start because CLI role assignment creation reused an existing principal/role/scope assignment and did not apply the requested verification condition. That attempt was stopped and cleaned, not counted as a passing access test. The coordinator now journals/restores a temporary verification-repository extension to an existing Reader condition and validates the ID/condition of genuinely new assignments. Effective access remains read-only; no wider role was used to obtain a pass.

Evidence: [identities and environments](evidence/delivery-identities-2026-11-03.json), [deployment read-back](evidence/delivery-permissions-deployment-2026-11-03.json), [SQL role checks](evidence/delivery-sql-access-2026-11-03.json), [developer-profile checks](evidence/delivery-developer-verification-2026-11-03.json), [actual group data reads](evidence/developer-group-reads-2026-11-03.json), [registry-token checks](evidence/delivery-registry-verification-2026-11-03.json), [final cleanup state](evidence/delivery-final-state-2026-11-03.json), [failed startup and remediation](evidence/delivery-verification-startup-failure-2026-11-03.json). The [Stage 1 checklist](../engineering/stage-1-completion-checklist.md) records remaining gates.
