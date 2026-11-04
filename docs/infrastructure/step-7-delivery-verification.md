# Development delivery verification

## GitHub results on 4 November 2026

- The release verification passed. GitHub built and published the image, signed in to Azure with OIDC, and verified setting and restoring the image configuration on the disabled Aquarium host. [Release run](https://github.com/PhilipTodd/azure-distributed-systems-reference/actions/runs/41735129057)
- The migration verification passed. GitHub installed the SQL client, signed in to the tenant with OIDC, connected to SQL, verified the Aquarium migration role, and created and read back the probe table before rolling back the transaction. [Migration run](https://github.com/PhilipTodd/azure-distributed-systems-reference/actions/runs/41739099738)

The running deployment check passed through the temporary APIM route described below. Diagnostics verification and legacy pipeline cutover remain open.

## Proposed Aquarium activation window

Use the exact image published by the successful release run. Its digest is `acradtplatformdev.azurecr.io/parameterpilot/aquarium-api@sha256:ac70bc6440656be94d273835bc14894bcbf873a43ba064e84cef9ade0e12e28f`. Readback on 4 November showed Aquarium disabled, an empty image setting, public access disabled, both main and SCM default deny, and managed identity registry pull enabled.

1. Recheck the baseline and snapshot the image, port, warm-up, health and logging settings before making changes. Use the owner-controlled Azure session for activation. Abort on unexpected baseline drift.
2. Set the digest, container port 8080, and platform warm-up path `/health` with HTTP 200 required. Temporarily enable the Aquarium host while retaining disabled public network access and default-deny main and SCM rules. The platform warm-up probe runs inside App Service. Bound the startup window to ten minutes.
3. Read platform container startup diagnostics via Azure Resource Manager. Record the image digest and successful warm-up or the failure category. The verification image tests startup and health. The existing managed identity configuration and vault tests are separate evidence of data access. Confirm the owner can read the diagnostic output and review logging categories and retention before any permanent logging change.
4. In cleanup, stop and disable Aquarium and restore the original image, app settings, health and logging configuration. Read back disabled public access, the main and SCM rules, and the original image. If automatic cleanup fails, use the saved snapshot to complete owner recovery before closing the window.

Approval covers only temporary Aquarium activation and restoration with this digest. Track any APIM or legacy cutover changes separately.

## Activation result on 4 November 2026

The owner approved the closed-host window. The first attempt stopped when Azure rejected the one-minute HealthCheckStatus interval. The retry used five-minute samples and temporary container logging. Azure reported the host running with the approved digest, but no current successful health sample arrived and the management logs contained no startup success tied to that digest. The runtime result is inconclusive. Aquarium was disabled and the original image, selected settings, logging and access rules were verified after cleanup. [Initial attempt](evidence/step-7-aquarium-activation-initial-2026-11-04.json) · [Retry](evidence/step-7-aquarium-activation-2026-11-04.json)

The owner approved the temporary PP-only APIM route. The same published image returned HTTP 200 through APIM with role Aquarium and run marker `github-41735129057-1`. A direct backend request returned 403. The temporary API was removed, the shared APIM policy matched its original value, and Aquarium was disabled with its original settings and access rules restored. Owner diagnostics review remains open. [APIM health evidence](evidence/step-7-aquarium-apim-health-2026-11-04.json)

The two manual GitHub workflows are prepared locally for review. Run them from the reviewed main revision and check the existing environment protections before dispatch. Both share one concurrency group and use the environment's individual OIDC identity. Review the image and SQL together with the workflows before approval.

The owner approved both verification tests in chat. The approved scope is publishing the verification image and testing image configuration on the disabled Aquarium host, plus executing the rollback-only Aquarium SQL probe. Each live run still goes through its protected GitHub environment after the workflows reach the reviewed main revision.

| Run | Expected evidence | Owner action |
| --- | --- | --- |
| Verify Development release | Locked restore with SDK 10.0.403, build with the existing digest-pinned ASP.NET image, push to the approved Aquarium repository, and verify the digest on the closed Aquarium host before restoring its original image configuration | Approve the reviewed `dev` job. Agree how long to keep the verification image. |
| Verify Development migration | Authenticate to ReferenceProjectsDb as the migration principal, verify AquariumMigrations membership, create and read back a synthetic Aquarium table inside a transaction, and roll back | Review the DDL and approve the `dev-migrations` job. Confirm the probe table is absent after execution. |

Check that the runner has ODBC Driver 18 and an approved network route to Azure SQL before approving the migration run. If the firewall rejects the runner, bring back an explicit connectivity proposal for review. The migration identity's permission boundary is the Aquarium schema.

The release probe leaves Aquarium disabled. Its configuration readback verifies the release identity's write permission, while container pull, startup, health and approved ingress require a separate owner-authorised activation window. Before that window, capture the host configuration, agree the expected scope of access and the health endpoint, and establish the rollback steps. If a run is interrupted during configuration, inspect the host's image setting and restore its original empty value through the owner-controlled recovery path. Keep the workflow run URL and published digest in the evidence.

## Diagnostics and cutover

Aquarium currently has no Azure Monitor diagnostic export. The owner session could read App Service detector metadata and metrics. The ARM container-log request timed out during the successful APIM test, so startup-log retrieval remains unverified.

Proposed diagnostic verification for owner approval: create the Aquarium-only diagnostic setting `pp-step7-aquarium-platform`, exporting only `AppServicePlatformLogs` to the existing `log-platform-dev` workspace in `rg-platform-dev` using resource-specific tables. The workspace default retention is 30 days. Check the effective table retention before approving ongoing collection. This creates a log ingestion path that may incur Azure Monitor charges. Exclude HTTP, application and console logs from this test. In a separately approved startup window, query the resource-specific table for that time range and confirm the owner can read startup events. Remove the test setting after verification. Already-ingested entries remain subject to workspace retention. Keep tokens, credentials, private keys and customer payloads out of logs.

The owner approved the temporary test on 4 November. The target table had 30-day effective retention and the owner session could query it. Aquarium was activated for two minutes and restored to its disabled baseline. The five-minute ingestion wait returned zero Aquarium events for the test window. The temporary export was removed and its absence verified. Ingestion remains unverified. Requery the original time window before considering another export. [Test evidence](evidence/step-7-aquarium-platform-diagnostics-2026-11-04.json) · [Azure Monitor diagnostic settings](https://learn.microsoft.com/en-us/azure/azure-monitor/platform/diagnostic-settings)

### Build verification

The build passed on the merged revision using SDK 10.0.403 and locked packages for all four verification projects. [GitHub build](https://github.com/PhilipTodd/azure-distributed-systems-reference/actions/runs/41744290569)

`build-stage1-verifiers.yml` builds the four existing .NET verification projects with locked packages and SDK 10.0.403. Its runner-local SDK configuration disables roll-forward and checks the resolved version. The GitHub release run already built and published the Aquarium probe using the digest-pinned ASP.NET runtime image. The repository currently contains verification projects and a static coming-soon page. Add the product build gates as product projects are introduced.

### Legacy delivery inventory and replacements

The owner-approved website run passed. The preflight matched the live content, the protected identity published it, and both custom domains served the expected page and image afterward. [Website verification](https://github.com/PhilipTodd/azure-distributed-systems-reference/actions/runs/41744447102)

| Legacy path | Replacement and acceptance |
| --- | --- |
| `infra/pipelines/deploy-ui-dev.yml` | `verify-dev-website.yml` uses the protected `dev` identity and an exact CLI version to republish `src/web/coming-soon` to the existing Static Web App production slot. It compares the live page and asset before publication and checks both custom domains afterward. Owner approval is required for the live publication. |
| `infra/pipelines/deploy-infra-dev.yml` | GitHub validates the Bicep and security boundaries. For infrastructure changes, the owner runs subscription validation, reviews what-if, then applies the reviewed PP Bicep revision and parameters in the owner-controlled session. Preserve an independent review gate between preview and apply. |

Both checked-in definitions have `trigger: none` and `pr: none` and refer to `sc-parameterpilot-dev`. Confirm Azure DevOps pipeline settings, schedules, queued runs and service connection consumers in the owner's organisation before retirement. Once the website replacement and owner infrastructure procedure are verified, agree a cutover window, disable the superseded manual pipelines, and preserve their settings for rollback. If a replacement fails, re-enable only the applicable legacy definition. Review service connection retirement separately after verifying all consumers and the rollback window.

### Verified cutover inventory on 4 November

Azure DevOps project `ausdatatech / Public Portfolio` has two Parameter Pilot definitions. Pipeline 13 is `pp - infra - dev` and pipeline 14 is `web - pp - dev`. Both queues are enabled and both definitions point at former YAML paths absent from main. Neither reported a configured schedule or active or queued run. The connection returned explicit permissions for IDs 13 and 14. Its 22 available execution records only named those definitions when a pipeline definition ID was present. [Inventory](evidence/step-7-legacy-inventory-2026-11-04.json)

The owner-run infrastructure replacement passed subscription validation. What-if reported `NoChange` for the resource group and `Modify` for the website and both custom domains. The preview includes deployment authentication, provider, inbound IP, traffic splitting, build properties and domain validation metadata. Treat these as preview differences requiring review before a future apply. The infrastructure test ended at what-if.

Proposed cutover for owner approval: recheck that IDs 13 and 14 still point at the expected Parameter Pilot repository and have no active or queued runs. Set only their queue status to `disabled` and verify both readbacks. Preserve the definitions and service connection. Roll back by setting the affected queue to its previous `enabled` status after rechecking the intended YAML path. The current legacy paths are missing, so enabling a queue alone would not restore a working run.

The owner approved the queue cutover. Both definitions passed the scope and queue preflight. Azure DevOps readback confirmed `disabled` at revision 3 for both definitions. The service connection remains available for the documented rollback.

A late Log Analytics query at 01:58 UTC returned zero Aquarium platform events for the original activation window. Owner query access passed. Central Log Analytics ingestion remains unverified.

The owner approved a temporary single-address SCM exception. After shortening the rule name to meet Azure's 32-character limit, the owner Entra session read the retained startup record for the earlier APIM verification deployment. The log named the exact GitHub-published image digest and recorded successful warm-up at 23:56:59 UTC on 3 November, which was 4 November in Sydney. Direct API access returned 403 and unauthenticated SCM access returned 401. The SCM exception was removed and the original disabled host, image, app settings and rules were verified. For Stage 1, the protected startup-log read supplies the diagnostics evidence. Centralised log collection remains a follow-up. [Startup log readback](evidence/step-7-aquarium-startup-log-readback-2026-11-04.json)

References: [GitHub OIDC setup](https://learn.microsoft.com/en-us/azure/developer/github/connect-from-azure-openid-connect), [App Service configuration API](https://learn.microsoft.com/en-us/rest/api/appservice/web-apps/update-configuration).
