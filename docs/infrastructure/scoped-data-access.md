# Aquarium SQL and Tracking Cosmos access

Date: 2 November 2026 | Status: Actual SQL/Cosmos workload verification passed on 3 November; later permission/delivery work tracked separately

## Scope and deployed results

Owner authorisation is recorded in [2 November decisions](../engineering/authorised-decisions-2026-11-02.md). Work is on codex/pp-scoped-data-access, branched from the existing readiness commit so the PR under owner review is not altered. Nothing has been committed/pushed on this new branch.

| Identity | SQL | Cosmos |
| --- | --- | --- |
| Aquarium API e43e0132-e184-4669-8431-9f5a3ea5393e | Contained EXTERNAL_USER api-adt-aquarium-dev; CONNECT and AquariumRuntime membership only; production object grants empty | No data assignment |
| Tracking API 6c046dfa-2416-4706-893d-7cc000afecf0 | No runtime user introduced | One custom data role, scoped to ReferenceProjects/parameterpilot-tracking |

## SQL security bootstrap

[001-bootstrap-aquarium-access.sql](../../infra/sql/001-bootstrap-aquarium-access.sql) creates the Aquarium schema owned by the isolated AquariumSchemaOwner role, not by a runtime account or shared dbo principal. Existing mismatched ownership/identity is rejected rather than reassigned. AquariumRuntime excludes DDL/user/role/schema administration and is distinct from AquariumMigrations. The migration role has schema ALTER and narrow object-creation capabilities, with no member assigned. AquariumSchemaOwner has no runtime members.

A verified managed-identity client/application-ID SID with TYPE=E creates the contained user without adding directory-reading grants to the SQL server. The owner CLI session resolves the client ID from the actual deployed identity object. The 2 November object-ID SID mapping was repaired after the 3 November real-login test exposed the mismatch. The runner obtains an individual Entra SQL token in memory, verifies tenant/subscription and resolves the actual deployed Aquarium principal before acting. It never copies workload credentials or prints tokens.

There are no domain tables yet. No schema-wide SELECT/INSERT/UPDATE/DELETE or built-in db_owner/db_datareader/db_datawriter membership is granted. Reviewed migrations must add object-level CRUD grants only on runtime tables. Keep EF migration history excluded; this bootstrap does not create an EF history table or grant runtime access to one.

```powershell
python -m pip install -r scripts/access-requirements.txt
# Default: read-only inspection.
python scripts/bootstrap-aquarium-access.py
# Explicitly authorised apply and transactional permission verification.
python scripts/bootstrap-aquarium-access.py --apply --verify --evidence docs/infrastructure/evidence/aquarium-sql-access-2026-11-02.json
```

Requires Azure CLI login as the authorised SQL administrator and ODBC Driver 18 with certificate validation. The script is fixed to Development tenant/subscription/server/database and its approved API host. Do not run as an ordinary developer or claim the administrator token is the runtime identity.

Live verification applied the bootstrap twice and confirmed idempotent final security state. EXECUTE AS the contained user performed synthetic object-scoped CRUD. It denied schema/role/user administration, database CONTROL, DDL, migration-probe reads/writes and zero-row reads of existing BlastPlanning/Ticketing tables. No customer rows were read. All synthetic tables and temporary object grants were created inside a transaction and rolled back; persisted Aquarium object and runtime object-grant counts are zero. [SQL evidence](evidence/aquarium-sql-access-2026-11-02.json).

EXECUTE AS tests effective SQL permissions, not token authentication from App Service. Actual managed-identity SQL login and final table grants must still be tested. No migration principal/CI identity has been fabricated or granted the migration role.

## Tracking container and custom role

[cosmos-container.bicep](../../infra/bicep/modules/cosmos-container.bicep) creates only three application-owned children on the existing shared Cosmos account: parameterpilot-tracking in ReferenceProjects, a custom role definition and a role assignment. The container uses /tankId Hash v2; no TTL or dedicated throughput is declared. Provider-default indexing is a starting container definition, not an application index/performance approval. State/idempotency/outbox must remain in the same container and logical partition.

The custom role has exactly readMetadata, items/create/read/replace/upsert/delete, executeQuery and readChangeFeed. There are no wildcards, stored-procedure/conflict-management actions or management-plane/throughput permissions. Its definitionâ€™s assignable scope is the account ceiling; its only assignment is the Tracking identity at the specific container data scope. A role definition is not an account-wide grant.

New main parameters deployTrackingDataAccess=false and trackingContainerName/PrincipalId are nonsecret. The live principal must be reverified if the host is replaced. The authorised deployment used only deployTrackingDataAccess=true, leaving deployServiceFoundations=false so stopped hosts/stores were skipped. The normal entry point remains infra/bicep/environments/dev/main.bicep; no independent deployment entry point was added.

Deployment pp-tracking-access-20261102-b31e7904 Succeeded. Readback verified exact assignment scope/action list, /tankId, no TTL, unchanged BlastIQ resource definition and unchanged shared 400 RU/s. No domain Cosmos records were read/written. [Cosmos evidence](evidence/tracking-cosmos-access-2026-11-02.json).

```powershell
az bicep build --file infra/bicep/environments/dev/main.bicep --outfile "$env:TEMP/pp-access-main.json"
az bicep build-params --file infra/bicep/environments/dev/main.dev.bicepparam --outfile "$env:TEMP/pp-access-parameters.json"
python scripts/verify-service-foundations.py "$env:TEMP/pp-access-main.json" "$env:TEMP/pp-access-parameters.json"
python scripts/verify-data-access.py "$env:TEMP/pp-access-main.json" "$env:TEMP/pp-access-parameters.json"
```

Five deliberately unsafe template mutations are rejected: wrong partition, dedicated throughput, TTL, account-wide grant scope and wildcard data actions. GitHub validation includes both compiled-template verifiers. No new shared-platform repository changes were made.

## Remaining completion gates

- Actual managed-identity SQL login and Cosmos SDK reads/writes/query/transactional batch, including explicit other-product/container/administration denials.
- Concrete Aquarium application migrations/tables, explicit per-object runtime grants and separate controlled migration principal/delivery path.
- Reproducible permission tests under actual workload execution: the hosts currently remain disabled without application images. Do not start or expose them, impersonate them through copied credentials or add temporary broad roles merely to pass tests.
- Ordinary developer access, deployment/registry rights and configuration/vault effective tests belong to the remaining Stage 1 work.

This work progresses step 1; it does not close Stage 1 or imply feature implementation readiness.

References: [SQL CREATE USER SID/TYPE](https://learn.microsoft.com/en-us/sql/t-sql/statements/create-user-transact-sql), [Cosmos data actions and SDK metadata/query requirements](https://learn.microsoft.com/en-us/azure/cosmos-db/reference-data-plane-security), [Cosmos container-scoped RBAC](https://learn.microsoft.com/en-us/azure/cosmos-db/how-to-connect-role-based-access-control).

## Actual managed-identity verification completed — 3 November 2026

[Current evidence](evidence/managed-identity-access-2026-11-03.json) closes authoritative Stage 1 step 1: Aquarium 20 passing checks and Tracking nine, executed inside the existing Azure hosts using ManagedIdentityCredential(SystemAssigned). Each token object ID matched the expected host. No owner CLI credential was available to the runtime.

Aquarium’s real SQL login initially failed because the previous user SID used the identity object ID. Microsoft’s SID/TYPE syntax requires a managed identity’s client/application ID. The guarded repair changed only that known legacy contained-user mapping to client ID 2602e7fc-ad33-46fc-b893-de79db7e2ef2, retaining runtime-only membership and CONNECT; Azure/Cosmos role assignments correctly retain object IDs. Passwords, other users, shared schemas and firewall settings were untouched. The bootstrap’s explicit repair option refuses unexpected ownership or permissions.

Fresh SQL authentication/object CRUD and migration/cross-product/DDL/admin denials passed. Tracking’s SQL login was denied; its own Cosmos CRUD/query, same-partition transactional batch, failed-batch no-partial-item check, BlastIQ-container denial and management denial passed. Synthetic Cosmos records were deleted by the workload. The coordinator removed both SQL probe tables/temporary object grants and all three repository-conditioned pull/publish assignments and verified their absence. The immutable private verification image is retained; no credentials are embedded in it.

Both hosts are disabled again, public access disabled, main/SCM default deny, original container settings/Always On and selected nonsecret settings restored. Logging is disabled at its original 35 MB quota; Azure retains a three-day value where the field was previously unset. That difference is explicit in the evidence and can be superseded by the intended diagnostics policy in step 7. Shared B1 remains one Linux worker.

The [probe source and recovery instructions](../../tests/Stage1.AccessProbe/README.md) and scripts/run-workload-access-verification.py make the run reproducible. Registry conditions are restricted to parameterpilot/access-verification. Logs are read through Azure management APIs with ingress still blocked; attempt timestamps exclude old cached results. Package restore/audit passed after pinning the patched cryptography dependency. The verification used the installed SDK 10.0.302 and a pinned .NET runtime image; this does not validate the separate candidate product SDK 10.0.403 baseline.

Earlier remaining-gate statements above are superseded for tracking by the [authoritative checklist](../engineering/stage-1-completion-checklist.md). Configuration/vault tests belong to step 2; migration/developer/deployment permissions and future table-specific grants belong to step 3. No Stage 2 domain features were implemented. No commit or push has been performed for this work.
