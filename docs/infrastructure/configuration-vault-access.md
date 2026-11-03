# Configuration and vault isolation verification

Date: 3 November 2026 | Status: Authoritative Stage 1 step 2 verified

## Actual identity results

[Evidence](evidence/configuration-vault-access-2026-11-03.json) records 30 passing checks from the existing closed hosts using only ManagedIdentityCredential(SystemAssigned). Each token object ID matched the expected Aquarium or Tracking managed identity. Owner CLI credentials were used only for setup, metadata inspection and cleanup, not for the runtime access tests.

| Per-host check | Result |
| --- | --- |
| Own App Configuration key read | Allowed; known synthetic value matched |
| Cross-service configuration read | Denied |
| Configuration create/update/delete | Denied |
| Own disposable secret read | Allowed; expected SHA-256 hash matched without logging the value |
| Cross-service secret read | Denied |
| Secret create/update/delete | Denied |
| Role-assignment administration write on own store/vault | Denied; attempted to PUT existing read-role assignments with unchanged properties |
| Resource-management write on own store/vault | Denied; attempted to PATCH existing tags unchanged |
| Explicit system identity/object ID | Matched expected host identity |

Metadata enumeration is not equivalent to administration. The initial probe expected metadata-list requests to be denied; those checks were replaced with actual idempotent write attempts. Final write tests all returned Forbidden. No runtime permissions were widened to satisfy a test. Every unexpected HTTP status remains a failure.

## Setup and cleanup scope

The owner authorised this run in [3 November decisions](../engineering/authorised-decisions-2026-11-03.md). Temporary permissions were two repository-conditioned host pulls, one repository-conditioned owner publisher, four owner content setup assignments at the individual PP stores/vaults, and two metadata-only Key Vault Reader assignments used to confirm asynchronous deletion after setup permissions had been removed. All nine were removed and their absence verified. Runtime roles remain own-store App Configuration Data Reader and own-vault Key Vault Secrets User only.

The test created only a nonce-prefixed Stage1:Step2 configuration key and pp-step2 secret in each service resource. A separate denied-create target in the same synthetic namespace was checked and cleaned if necessary. Random secret values stayed in memory; expected hashes were used inside the private image and are not included in the evidence. No real settings, secret values or credentials were inspected.

Configuration keys and active test secrets are absent after cleanup. Two disposable secrets remain soft-deleted, with metadata showing their deletion and scheduled purge under existing retention/purge protection. No purge was attempted. Secret deletion is asynchronous; cleanup now waits for deletion metadata before removing owner setup access and retains that access for retry if cleanup fails. The final check used metadata-only deleted-secret listing, which does not return secret values.

Both API hosts returned to enabled=false/publicNetworkAccess=Disabled, main and SCM default Deny, original empty image configuration, original Always On/selected settings and original logging state. Logging retained this run’s original three-day/35 MB disabled setting; the earlier unset-to-three-day normalization belongs to step 1 and was not introduced again here. Stores remain Free/key-auth-disabled; vaults retain RBAC, purge protection and 90-day soft delete. Resource tags and permanent read grants are unchanged. No SQL password, database, Cosmos data or shared-plan setting was modified in this mode.

## Reproduction and evidence

Source: [probe](../../tests/Stage1.AccessProbe/README.md), [coordinator](../../scripts/run-workload-access-verification.py). Build/publish the probe, then use the explicitly authorised configuration mode:

```powershell
dotnet restore tests/Stage1.AccessProbe/Stage1.AccessProbe.csproj --locked-mode
dotnet publish tests/Stage1.AccessProbe/Stage1.AccessProbe.csproj -c Release --no-restore --no-self-contained -o tests/Stage1.AccessProbe/.runtime/publish
python scripts/run-workload-access-verification.py --phase all --mode configuration
```

The ignored journal records exact restoration and temporary-assignment IDs before changes; --phase cleanup can be retried and is idempotent after completion. Management-plane log retrieval keeps ingress blocked and filters stale results by run/role/attempt timestamp. A private image by immutable digest is retained as a reproducible artifact; temporary Docker authentication is removed. No Git publication or merge occurred during this work.

This verifies access controls, not application configuration-provider loading, secret rotation/refresh or outage behaviour. Those behaviours remain implementation work. Step 3 covers controlled migration/developer/deployment permissions; the [authoritative checklist](../engineering/stage-1-completion-checklist.md) governs the remaining scope.

References: [App Configuration Entra data-plane permissions](https://learn.microsoft.com/en-us/azure/azure-app-configuration/rest-api-authorization-azure-ad), [Key Vault RBAC](https://learn.microsoft.com/en-us/azure/key-vault/general/rbac-guide), [deleted-secret metadata listing](https://learn.microsoft.com/en-us/rest/api/keyvault/secrets/get-deleted-secrets/get-deleted-secrets).
