# Development delivery verification

The two manual GitHub workflows are prepared locally for review. Run them from the reviewed main revision and check the existing environment protections before dispatch. Both share one concurrency group and use the environment's individual OIDC identity. Review the image and SQL together with the workflows before approval.

The owner approved both verification tests in chat. The approved scope is publishing the verification image and testing image configuration on the disabled Aquarium host, plus executing the rollback-only Aquarium SQL probe. Each live run still goes through its protected GitHub environment after the workflows reach the reviewed main revision.

| Run | Expected evidence | Owner action |
| --- | --- | --- |
| Verify Development release | Locked restore with SDK 10.0.403, build with the existing digest-pinned ASP.NET image, push to the approved Aquarium repository, and verify the digest on the closed Aquarium host before restoring its original image configuration | Approve the reviewed `dev` job. Agree how long to keep the verification image. |
| Verify Development migration | Authenticate to ReferenceProjectsDb as the migration principal, verify AquariumMigrations membership, create and read back a synthetic Aquarium table inside a transaction, and roll back | Review the DDL and approve the `dev-migrations` job. Confirm the probe table is absent after execution. |

Check that the runner has ODBC Driver 18 and an approved network route to Azure SQL before approving the migration run. If the firewall rejects the runner, bring back an explicit connectivity proposal for review. The migration identity's permission boundary is the Aquarium schema.

The release probe leaves Aquarium disabled. Its configuration readback verifies the release identity's write permission, while container pull, startup, health and approved ingress require a separate owner-authorised activation window. Before that window, capture the host configuration, agree the expected scope of access and the health endpoint, and establish the rollback steps. If a run is interrupted during configuration, inspect the host's image setting and restore its original empty value through the owner-controlled recovery path. Keep the workflow run URL and published digest in the evidence.

## Diagnostics and cutover

Review the diagnostic policy during the activation window. Record the workflow run ID, image digest, target, health status and rollback result. Verify the owner's access to application and deployment diagnostics with an actual read. Keep bearer tokens, credentials, private keys and customer payloads out of logs. Review diagnostic categories and retention before changing collection settings.

The legacy Development definitions are `infra/pipelines/deploy-infra-dev.yml` and `infra/pipelines/deploy-ui-dev.yml`. The GitHub probe covers API image publication and a bounded SQL check. The inventory must map each active legacy trigger and credential to its replacement before retirement. In particular, infrastructure maintenance remains an owner operation and the website publishing path needs its own verification. After successful replacement runs, agree a cutover window with the owner, pause the superseded triggers and verify the new path. Re-enable the prior trigger if rollback is needed. Review credential retirement separately once rollback is no longer required.

References: [GitHub OIDC setup](https://learn.microsoft.com/en-us/azure/developer/github/connect-from-azure-openid-connect), [App Service configuration API](https://learn.microsoft.com/en-us/rest/api/appservice/web-apps/update-configuration).
