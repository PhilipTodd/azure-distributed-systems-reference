# Hybrid Local development and developer access

Version: 0.3 | Date: 21 October 2026 | Status: Accepted approach; runnable setup/tool inventory pending

Authority: [ADR-029](../architecture/decisions/adr-029.md). Initial environments are [Local/dev](environments.md).

## Dependency strategy

Run service code and practical databases/storage locally; use emulators only for verified supported behaviour. Unit/failure tests use deterministic doubles. Use selected approved dev Azure dependencies for identity or unsupported local features, and run real Azure integration checks before accepting broker/security/transaction behaviour. In-memory substitutes do not establish cloud parity.

Exact emulator images, supported host platforms, endpoints, versions and setup/check commands remain to be selected. No runnable Compose or project commands are invented here.

## Developer identity

Use each developer's own Microsoft Entra identity and scoped dev permissions via an approved Azure CLI/Visual Studio or equivalent login. Do not copy App Service/worker credentials or share a developer account. Keep migration/administration elevation separate. Aquarium-owner sign-in remains External ID; developer resource access is not that customer flow.

Managed identity is the deployed workload approach, not assumed to exist on a developer machine. Unavoidable local credentials stay in User Secrets/equivalent untracked settings; no production credentials/data. Concrete roles, login selection, tooling and access verification remain pending.

## Acceptance evidence

A fresh developer can follow reproducible instructions, start the approved local dependencies, run deterministic tests, access only permitted dev services with their own identity and demonstrate emulator/cloud differences. No credentials enter source/logs/browser build. Record commands/results only once runnable assets exist.

See [configuration policy](../infrastructure/configuration-and-secrets.md) and [technology baseline](../engineering/technology-baseline.md).

## Stage 2 identity configuration — accepted 21 October 2026

ID-15/[ADR-009](../architecture/decisions/adr-009.md): register explicit localhost redirects and use a separate local Tracking OBO certificate, private key outside source control with appropriate permissions. Development uses its registered certificate protected in Key Vault; runtime/developer permissions remain least privilege. Both public certificates must be registered appropriately. Actual paths/thumbprints/loading/rotation/compatible tooling remain setup tasks. Never copy private credentials into browser assets or documentation.

## Minimum Stage 2 Local setup — accepted 21 October 2026

DEV-03: minimum Stage 2 Local setup runs Angular UI and Aquarium/Tracking APIs directly through development tooling. Docker Compose starts SQL Server Developer and Cosmos DB NoSQL emulator containers; use a small repeatable synthetic seed set. Actual Development External ID supports customer authentication/OBO. Select/pin supported compatible container/tool versions after verification; no preview assumption or floating latest pin. Local certificate and secrets follow ID-15/ADR-027.

Emulator/container results are not proof of Azure parity. Verify required operation support, including same-container/partition transactions, and real Development identity/permissions/cloud behaviour. If a required operation is unsupported locally, use the approved Development dependency for that check rather than building an inaccurate substitute. No unapproved resource creation/spend implied.

Advisor/PostgreSQL/photo dependencies wait for their stages. Add Service Bus and workers when the authorised implementation slice requires them; preserve core synchronous transaction/outbox design and do not fabricate broker-delivery evidence. Docker Compose manages dependencies, not a requirement to containerise local UI/APIs. No Compose file, dependencies, seeds, projects or resources created in this documentation update.
