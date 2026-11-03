# Stage 1 real managed-identity access probe

This is a non-feature verification host, not Aquarium/Tracking application implementation. It runs only on the two existing closed Development hosts, uses ManagedIdentityCredential with an explicit SystemAssigned identity (or an explicitly selected temporary user-assigned identity for the developer-profile mode), checks the token object ID against the expected identity and never falls back to a developer/CLI/environment credential. It prints only nonsecret test results; SQL exceptions are reduced to error numbers and Cosmos exceptions to status/substatus. Access tokens, identity endpoint headers, passwords and customer records are never logged.

Step 3 modes are coordinated by `scripts/run-delivery-access-verification.py`: developer tests use the approved read-only profile on a temporary identity, and registry tests examine actual ACR-issued repository token actions under each API identity. They do not authenticate the Entra developer group or the GitHub release/migration principals. Existing registry Reader assignments cannot be duplicated for another condition at the same principal/role/scope: the coordinator journals and temporarily extends their read condition to the one verification repository, then restores the original properties exactly. New temporary assignments must be checked against the requested ID/condition; CLI success alone is insufficient.

The coordinator runs locally under the authorised owner CLI session and obtains SQL admin tokens only to create/drop synthetic test objects. It does not use or reset the SQL administrator password. SQL runtime authentication inside the image uses each host’s own managed identity.

## Cases

- Aquarium actual SQL login, object-level CRUD, denied migration-table operations, denied DDL/admin roles and denied zero-row cross-product reads.
- Aquarium denied Tracking Cosmos access.
- Tracking denied SQL login; own-container CRUD/query and same-partition transactional batch; failed-batch atomicity and denied BlastIQ container access.
- Both identities denied Cosmos management-plane throughput-settings read.
- Synthetic Cosmos records deleted in the workload; SQL probe tables and object grants removed by the local coordinator.

## Run and recovery

Before executing, obtain applicable human authorisation for temporary host activation, repository-conditioned image pull/publish grants and synthetic data. No public ingress or SCM rule is opened. Always On is temporarily enabled to warm the host and restored afterwards. The same shared B1 plan is retained; only one verification host is run at a time.

```powershell
python -m pip install -r scripts/access-requirements.txt
dotnet restore tests/Stage1.AccessProbe/Stage1.AccessProbe.csproj --locked-mode
dotnet publish tests/Stage1.AccessProbe/Stage1.AccessProbe.csproj -c Release --no-restore --no-self-contained -o tests/Stage1.AccessProbe/.runtime/publish
python scripts/run-workload-access-verification.py --phase all
```

Requires Docker, Azure CLI, .NET 10 SDK, ODBC Driver 18 and an authorised Entra SQL administrator session. The runtime base image is pinned by digest and SDK dependencies by package lock. This verification build uses the locally installed SDK; it does not change or establish the product SDK baseline.

The ignored .runtime/journal.json stores restoration state and exact generated resource IDs before changes. It contains no credentials. --phase all has finally cleanup; individual prepare/publish/run phases are available for diagnosis. After interruption, run:

```powershell
python scripts/run-workload-access-verification.py --phase cleanup
```

Do not remove the journal before successful cleanup. Cleanup stops/disables hosts, restores original image/configuration/selected nonsecret settings/logging and removes only this run’s SQL objects and repository role assignments. The verification image remains as an immutable private registry artifact; it contains no credentials. Temporary Docker authentication is isolated and logged out/removed after push. Management-plane logs are obtained with ingress still blocked. Results are filtered by run ID, role and attempt start time to exclude retained old logs.

A failed test must be reported and corrected without broadening privileges. In particular, SQL SID/TYPE for a managed identity uses the verified client/application ID, while Azure RBAC/Cosmos assignments use its object ID. The 2 November SQL bootstrap’s object-ID SID mapping was detected by this actual-login test and repaired within its existing runtime-only permission boundary.

Actual results and cleanup verification are recorded separately in docs/infrastructure/evidence/. These checks do not implement configuration/vault tests (step 2), migration/developer/deployment permissions (step 3), customer identity, ingress readiness, Local bootstrap or final Stage 1 acceptance.

## Recorded run — 3 November 2026

Run 701b1d1e3ab6 passed all 29 real-identity checks after correcting the contained SQL SID/client-ID mapping. All synthetic SQL/Cosmos data and temporary registry/object grants were removed; hosts returned to disabled/closed state. The original 35 MB log quota and disabled logging were restored; Azure retains a three-day default where retention was previously unset. This is documented as a representation difference, not an exact nullable-field restoration. See [evidence](../../docs/infrastructure/evidence/managed-identity-access-2026-11-03.json).

Azure.Identity 1.21.0 and Cosmos 3.63.3 use accepted baseline SDK packages. The verification-only SqlClient 6.1.3 explicitly references Newtonsoft.Json 13.0.4 and System.Security.Cryptography.Pkcs 10.0.14; dependency audit found no known vulnerable packages after fixing the initial 9.0.4 transitive cryptography dependency. The local build SDK was 10.0.302; the product candidate SDK 10.0.403 remains to be verified separately. Runtime base image and deployed verification image are pinned by digest.

## Step 2 configuration/vault mode

The owner separately authorised step 2. Run the coordinator with --phase all --mode configuration after publishing the updated probe. This mode does not connect to SQL or Cosmos and creates no SQL probe tables. It creates only a run-specific synthetic key/value in each service store and a random disposable test secret in each service vault. The image receives only the expected secret hashes, never secret values. It uses the same explicit system-assigned identities and closed host lifecycle.

The owner CLI identity temporarily receives App Configuration Data Owner and Key Vault Secrets Officer at the individual PP store/vault scopes to set up and delete test content. Workload read assignments are unchanged. The same single-repository ACR conditions restrict temporary image publication and host pulls. All temporary assignments are journalled and removed after content cleanup; if content cleanup fails, owner setup access is retained for retry instead of orphaning test data.

Each host tests own configuration/secret reads; cross-service read denial; denied synthetic create/update/delete operations; denied no-op resource tag PATCH; and denied PUT of its existing read-role assignment with unchanged properties. Merely listing role-assignment metadata is not an administration-write test; the first probe design was corrected accordingly. Existing read-role payloads and resource tags are snapshotted so an unexpected success cannot introduce a new privilege or change the intended tags. Unexpected HTTP responses are failures, not accepted as denials.

Cleanup deletes only this run’s two known configuration-key names and two known secret names per resource (the primary and a denied-create target). Active test secrets must be absent afterwards. Deleted synthetic secrets can remain soft-deleted under the existing 90-day retention/purge protection; no purge is attempted. Only deletion metadata, checks and nonsecret identity/resource IDs go into evidence. Real configuration/secret contents, passwords and tokens are not logged. Application startup providers, rotation and failure semantics remain application implementation work.

Recorded configuration run 52b4dd5d34e2 passed 30 checks using the corrected administration-write tests. Temporary content/setup/registry access and two extra metadata-only cleanup Reader roles were removed (nine assignments total). Synthetic keys and active secrets are absent; two disposable secrets are soft-deleted under existing protection. [Step 2 evidence](../../docs/infrastructure/evidence/configuration-vault-access-2026-11-03.json) records controls and cleanup without secret values/hashes. Configuration mode is now available but does not implement production providers or rotation.
