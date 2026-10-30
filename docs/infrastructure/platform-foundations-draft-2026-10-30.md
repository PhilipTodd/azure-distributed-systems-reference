# Platform APIM/ACR deployment evidence — 30 October 2026

Status: Successfully deployed through main.bicep; infrastructure checks passed; Stage 1 remains open.

The owner explicitly approved the full deployment including the three pre-existing Cosmos/Insights what-if Modify entries. Deployment platform-dev-20261030-apim-acr-020536 used azure-reference-platform's established main.bicep and actual main.dev.local.bicepparam. It completed at 13:32:31 Sydney time on 30 October (02:32:31 UTC), taking 26 minutes 50.8 seconds. Correlation ID: 68290fd5-2ad9-4bd1-9c5c-d88446ee0074; Azure template hash: 12008029426972160106. No Git commit, merge, push or PR occurred.

Verified additions in rg-platform-dev / Australia East:

- apim-adt-platform-dev: classic Developer, one unit, system-assigned identity; gateway https://apim-adt-platform-dev.azure-api.net, observed public address 4.254.91.56. Legacy TLS protocols disabled inbound/backend; global 503 bootstrap policy installed.
- acradtplatformdev: Basic, admin and anonymous access disabled, repository ABAC mode; acradtplatformdev.azurecr.io rejects anonymous /v2/ with 401.

The unconfigured gateway root returns 404. Azure's provider-created Echo sample requires a subscription and rejects unauthenticated access with 401; no Parameter Pilot routes, subscription keys or application workloads were introduced. Backend source-address rules, workload image pull, JWT/OBO and owner-isolation journeys remain unverified.

Post-completion selected plan, SQL, Cosmos/400 RU and existing web/Function App snapshots exactly match pre-deployment. All seven Cosmos default/endpoint fields flagged as omitted in what-if remain unchanged. Existing blastplanning-events retains /streamId. B1 remains one worker; diagnostic tables retain 90 days. Existing apps remain Running; web/API root responses demonstrate reachability only, not business-journey correctness.

Platform repository records: docs/deployment-2026-10-30.md and docs/evidence/platform-deployment-2026-10-30.json. Reviewed source hashes identify the deployed working-tree source; no merged Git revision is claimed. Temporary compiled local parameters were deleted; no secrets were stored in evidence. The initial automatic-review rejection was followed by explicit owner approval and successful execution; no rejection workaround was used.

Only deployment/approval/evidence/runbook documentation changed during execution; infrastructure definitions were the previously reviewed main.bicep integration. Stage 1 still requires configuration/vault topology decisions, scoped access, Local/application bootstrap, ingress/identity/delivery checks and handover. PostgreSQL remains deferred to Stage 5. Budget remains approximately A$120/month total before tax/new variable usage; no actual final bill or hard cap is claimed.
