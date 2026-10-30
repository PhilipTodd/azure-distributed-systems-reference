# Stage 1 scoped-access setup

Date: 30 October 2026 | Status: Shared SQL administrator deployed and verified; scoped application access pending

This is the next item after configuration/vault ownership was accepted and provisioning deferred to PP Bicep. The owner subsequently instructed implementation to proceed. The dedicated administrator group and server assignment are now deployed; PP runtime roles and contained users remain pending.

## Current read-only evidence

- sql-adt-platform-dev now uses sg-adt-platform-sql-admins-dev (object ID 469d4226-c4a4-4cc1-8b99-58e1dfd595f7) as Entra administrator. Philip Todd is verified as owner/member; his token-based connection to ReferenceProjectsDb passed. Existing SQL authentication and firewall rules were preserved.
- cosmos-adt-platform-dev has no Cosmos SQL data-plane role assignments.
- Initial inspection found no matching administration group; the authorised bootstrap created and verified the dedicated group. This was not an audit of all directory elevation paths.
- No user-assigned identity was returned for rg-parameterpilot-dev. Aquarium/Tracking runtime apps and identities are not yet deployed; do not fabricate principal IDs or create unused worker identities.
- The signed-in owner is Philip Todd, philip.todd@ausdatatech.com.au, object ID 7233cead-7a49-4ab1-80f9-6066a03d193f.
- The owner selected "Dedicated platform SQL administrators group" when asked which Entra identity should administer the shared SQL server.

## Proposed concrete setup

| Area | Setup to prepare/apply under the applicable scoped authorisation | Boundary |
| --- | --- | --- |
| Shared SQL administration | Deployed security group sg-adt-platform-sql-admins-dev, with the confirmed owner account as owner/member; verified server Entra administrator. | Shared-platform bootstrap, separate from app data-plane grants. Preserve existing SQL auth, firewall and other projects. Group object ID is recorded above; no PP runtime members were added. |
| Aquarium runtime | Distinct app managed identity and contained database user; required rights only on approved Aquarium runtime objects/schema. | No db_owner/db-wide reader/writer, other-service schemas or DDL. Keep migration metadata out of runtime write permissions. |
| Aquarium migrations | Separate controlled identity/bootstrap operation; narrowly scoped Aquarium migration rights after actual schema/tables are specified. | No runtime elevation. Do not invent migration objects or run migrations now. |
| Tracking runtime | Actual Tracking identity with Cosmos data role limited to its approved container(s) within ReferenceProjects. | No account/database-wide data access, blastplanning-events or throughput management. Accepted partition is /tankId; panel/idempotency/outbox local atomicity retained. |
| Developer | Individual Entra login with explicitly scoped Development data/config access, distinct from customer External ID. | No copied workload credentials. The owner's membership in the admin group is privileged and cannot demonstrate nonadmin denial tests. |
| Application deployment | PP resource/content permissions and approved ACR repository access; trusted repo/environment OIDC, separate from runtime and platform deployment. | No reuse of subscription Contributor/Owner, broad role-assignment authority or other-project registry/data access. |
| Configuration/secrets | Actual PP-owned stores/vaults and runtime/content grants when PP Bicep is altered. | Deferred by owner; no shared-platform configuration/vault provisioning or placeholder grants now. |

The administrator group is privileged across the shared SQL server, including other products' databases. Its ownership/membership must be explicit; membership is not a substitute for scoped ordinary developer access. Do not assume eligible/PIM activation, extra licensing or a separate admin account has been configured. Use the actual app identities or a separately authorised scoped test principal for negative access tests, never the privileged owner session as proof of isolation.

## Implementation sequence

1. Review exact group name, initial owner member and server assignment. Create/verify the directory group without adding unrelated members; maintain its object ID as a nonsecret platform input. Then add the SQL Entra administrator setting through the established platform main.bicep/local/GitHub parameter paths and reviewed what-if. This document records the setup; it does not execute it.
2. Bootstrap approved Aquarium schema/data-plane users through a controlled SQL session once actual app/migration identities exist. Schema ownership must not implicitly confer broader permissions. Azure management Contributor does not establish SQL data access.
3. Finalise PP's real Tracking container name, identities and container-scoped data actions with PP Bicep. Create roles/assignments only for actual principals/scopes; preserve the other-project container. Built-in Data Contributor versus a narrower custom role must match the needed SDK actions and be tested.
4. Verify required access and explicit cross-service/cross-project/admin denials under the effective identities. Record object/resource IDs, grant manifests and safe results; never keys/tokens/passwords or customer data.
5. Keep remaining future identity, Local bootstrap, OBO, ingress and CI delivery tests with their respective steps. Do not claim Stage 1 access readiness from a directory group or management-plane role alone.

## Verification gates and sources

Required tests: Entra SQL admin login, ordinary/runtime database scope, migrations separated from runtime, Tracking allowed-container reads/writes/transactions and denied other-container access, no runtime administration, scoped registry pull/publish and developer access. The Entra SQL administrator login passed; all remaining scoped application/developer and isolation tests are pending.

Microsoft references: [SQL Entra configuration](https://learn.microsoft.com/en-us/azure/azure-sql/database/authentication-aad-configure), [Entra SQL identity considerations](https://learn.microsoft.com/en-us/azure/azure-sql/database/authentication-aad-overview), [Cosmos data-plane scopes](https://learn.microsoft.com/en-us/azure/cosmos-db/nosql/how-to-connect-role-based-access-control) and [data actions](https://learn.microsoft.com/en-us/azure/cosmos-db/nosql/reference-data-plane-security). Use actual supported syntax/IDs at implementation; do not broadly grant directory-reading permissions merely to avoid resolving a specific bootstrap issue.

The accepted dedicated-group approach is recorded in the [owner decision record](../engineering/authorised-decisions-2026-10-30.md). Instance ownership/deployment timing is [ADR-031](../architecture/decisions/adr-031.md).

## Administrator deployment outcome

Shared-platform deployment `platform-sql-entra-admin-20261030-051009` succeeded. The repeatable directory bootstrap, existing Bicep entry point, nine passing offline tests and safe live evidence are documented in the platform repository at `docs/sql-entra-administration.md` and `docs/evidence/sql-entra-admin-2026-10-30.json`. This completes the administrator prerequisite, not the Stage 1 scoped-access gate.

## Next scoped-access prerequisite check — 30 October 2026

After the administrator setup, live metadata inspection confirmed:

- rg-parameterpilot-dev contains only stapp-adt-parameterpilot-dev (Static Web App). No PP App Service apps or user-assigned managed identities were returned.
- ReferenceProjectsDb has no Aquarium schema and no Aquarium schema objects. Only system metadata was queried; no customer records were read or changed.
- Therefore no Aquarium runtime/migration principal or Tracking runtime principal is available for effective scoped-access tests. Do not substitute the privileged owner, invent principal IDs or grant access to unused worker identities.

The next dependency is PP infrastructure preparation through its existing main.bicep: actual Aquarium/Tracking hosting and identities, the accepted service-owned configuration/vault instances, and the approved Tracking container. Prepare concrete settings/preview for review, preserving shared B1 and other products. Create schema/contained users and narrow migration/runtime grants only against verified identities and approved objects; do not grant db_owner or general schema-wide DML over migration metadata merely to make a connection test pass. Application feature implementation remains a separate gate.

Publication evidence: PP readiness commit 18df4cb and shared-platform administrator commit e2b28b4 were pushed to their task branches. Platform [Validate Infrastructure](https://github.com/PhilipTodd/azure-reference-platform/actions/runs/41008801397) passed for e2b28b4; no workflow run was returned for the PP task branch. PP local checks passed schema meta-validation, 12 accepted seed shapes and 42 structural cases; these do not verify runtime or Azure access isolation.
