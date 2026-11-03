# Parameter Pilot Local dependencies

Status: the approved image pair passed [clean setup and restart verification](../docs/infrastructure/evidence/local-bootstrap-verification-2026-11-04.json) on 4 November 2026. The owner also verified startup, all nine checks and shutdown using SQL port 15433. Approval is recorded in `baseline.json`. Authority: [SPEC-04](../docs/engineering/stage-2-readiness-specification.md) and [ADR-029](../docs/architecture/decisions/adr-029.md).

## Prerequisites

Run from the repository root in PowerShell. Docker Desktop must be running with Linux containers on x64; Docker Compose, Python 3.14 and a .NET 10 SDK must be on PATH. Exploratory tests used Docker Desktop 4.96.0/Engine 29.9.1, Compose 5.6.0 and SDK 10.0.302. The accepted product SDK is 10.0.403; product SDK/runtime pinning remains Step 7. Node/Angular are not required just to start the databases.

Compose accepts SQL Server's container EULA and selects Developer edition for nonproduction use. Allow enough Docker memory for SQL's 2 GiB configured buffer limit plus process overhead and Cosmos; no host-wide Docker setting is changed automatically. The setup consumes this PC's resources, not Azure capacity.

## Commands

The approved startup sequence is:

```powershell
python scripts/local-development.py up
python scripts/local-development.py check
python scripts/local-development.py down
```

If another service uses SQL port 1433, set `$env:PP_SQL_PORT = '15433'` in PowerShell before running the same commands. Choose a free port and use the same PowerShell session for all three commands.

`up` creates dedicated project `pp-local` with persistent volumes, generates an independent Local SQL password, checks readiness and effective loopback-only port bindings, and pins the emulator's public certificate. SQL: `127.0.0.1:1433`. Cosmos: `https://localhost:8081`. Proposed emulator health: `http://127.0.0.1:18080/ready`; Explorer: `http://127.0.0.1:11234`. If a port is occupied, identify its owner; never stop another application automatically or silently change accepted ports.

`check` restores the committed package lock and runs the .NET verifier: repeatable synthetic seeds, SQL rollback, Cosmos partitioning, stale ETag rejection and same-partition transactional commit/rollback. `down` removes only this project's containers/network, preserving its volumes and password. Repeat `up` and `check` after stopping to verify persistence. Do not use Docker prune or delete other projects' volumes.

For a fresh-volume test:

```powershell
python scripts/local-development.py verify-clean
```

This uses a new `pp-local-check-<random-id>` project on separate ports 25433/28081/28080/21234, tests before and after container recreation, then removes only its own newly created test volumes in `finally`. Ordinary `pp-local` data is untouched. Do not run two fresh checks concurrently because they share these test ports. Evidence contains no passwords or personal data.

## Credentials and TLS

The random SQL password exists only in ignored `local/.runtime/<project>/sql-password`. Windows ACLs restrict the runtime directory to the current user; POSIX permissions are 0700/0600. Compose mounts it as a file, not a password value in manifests/arguments. The SQL process receives its required password in memory. Local administrators can inspect local resources; this is not a production secret store. Do not print, share or commit runtime files. Keep the password with its SQL volume; removing only one breaks login. Never reuse an Azure SQL password.

`sa` is bootstrap/test administration only, not the proposed Aquarium runtime account. Service-owned Local users and actual migrations follow their authorised implementation. No Azure SQL login or password is read or changed.

The coordinator captures the public emulator certificate over a fixed loopback socket and records its SHA-256 pin. SDK calls require that exact certificate on that Local port. There is no global certificate-validation bypass or trust-store change. `up` refreshes the pin after recreation. SQL's self-signed certificate is accepted only by the verifier's hard-coded loopback connection.

The approved GA vNext emulator does not enforce authentication. The SDK uses a Local placeholder key, not an Azure account key. Loopback binding and synthetic data are mandatory. Managed identity, permissions, RU/index performance and cloud-specific behaviour require approved Development Azure checks; emulator success is not cloud security evidence.

## Fixtures and application boundaries

`synthetic-fixtures.json` names only database `ParameterPilotLocalBootstrap`, SQL `LocalBootstrap.SyntheticFixture` and Cosmos container `local-bootstrap` with `/tankId`. Two synthetic records contain no customer identity or personal data. Temporary batch-test records are removed. Rerunning `check` restores only the reserved fixtures without duplicates; it does not erase other data or provide a general database reset.

The accepted twelve scientific definitions remain in `docs/api/schemas/stage-2-seed-proposal.json`. They are not installed into invented business tables. Actual migrations/container definitions/seeds are delivered with Stage 2 features. Product UI/API startup commands do not exist yet; the Stage 1 probes are separate tooling. No ownership, profile or measurement feature is claimed here.

Real Development External ID and the separate non-exportable Local OBO certificate remain the identity dependencies: [setup](../docs/infrastructure/customer-identity-setup.md). Individual Azure developer access is distinct from customer sign-in; Steps 1–4 record the effective access/denial evidence. No broader permissions or deployed workload credentials are needed by this setup.

Sources: [SQL container setup](https://learn.microsoft.com/en-us/sql/linux/quickstart-install-connect-docker), [Cosmos GA announcement](https://devblogs.microsoft.com/cosmosdb/announcing-general-availability-of-the-azure-cosmos-db-vnext-emulator/), [emulator limitations](https://learn.microsoft.com/en-us/azure/cosmos-db/emulator-linux).
