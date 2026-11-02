# Authorised decisions — 30 October 2026

## PP-exclusive configuration/vault ownership and deferred deployment

Evidence: after the owner challenged platform ownership and the assistant recommended PP ownership of exclusive instances, the owner stated: “Agreed. We will deploy the App Config and Key Vaults when we alter the PP repository bicep files. Update the documentation and proceed with the next item.”

Accepted: PP owns and deploys its service-exclusive App Configuration stores and Key Vaults through PP Bicep when that infrastructure is altered; shared-platform provisioning of these instances is not a prerequisite. Service isolation/least privilege remain. [ADR-031](../architecture/decisions/adr-031.md) supersedes the earlier platform-managed proposal and refines ADR-024/027. No instance, secret or grant was created by this documentation task.

## Dedicated shared SQL administrator group

Evidence: for the next scoped-access step, the owner selected “Dedicated platform SQL administrators group” in response to a question recommending a group containing the owner's account as the shared SQL server's Entra administrator, separate from PP runtime access.

The [scoped-access plan](../infrastructure/scoped-access-readiness.md) records a candidate group name, confirmed owner account and server/database/container boundaries. The owner subsequently replied “Proceed” to the described repeatable directory bootstrap and existing Bicep server-configuration approach. Group sg-adt-platform-sql-admins-dev (469d4226-c4a4-4cc1-8b99-58e1dfd595f7) was created with the confirmed owner as owner/member and configured as server Entra administrator. Deployment platform-sql-entra-admin-20261030-051009 succeeded and a token-based owner SQL login passed. Existing SQL authentication, server settings and firewall rules were preserved. PP scoped runtime/migration/developer grants remain pending.

## Full platform deployment including reviewed existing-resource updates

Outcome: deployment `platform-dev-20261030-apim-acr-020536` subsequently Succeeded at 13:32:31 Sydney time. APIM/ACR infrastructure controls and selected unchanged shared-resource snapshots were verified; see [deployment evidence](../infrastructure/platform-foundations-draft-2026-10-30.md). This outcome does not close the remaining Stage 1 access/application readiness gates.

Evidence: after the assistant explicitly asked whether the owner approved the full main.bicep deployment including Cosmos account/database and Application Insights updates alongside APIM/ACR, the owner replied “I approve. Proceed with the deployment.”

This authorises the existing subscription-scope main.bicep/local-parameter path, APIM Developer/policy and ACR Basic additions, and the three specifically reviewed pre-existing Modify deltas. It does not approve other new updates, deletion, scaling, store separation, broad grants or retention reduction. Refreshed validation and preview matched the approved scope. Azure accepted deployment `platform-dev-20261030-apim-acr-020536`; successful completion and operational checks remain distinct evidence. No source merge/push/PR operation is authorised or implied by this deployment record.

## Revised development hosting budget accepted

Evidence: after presentation of A$118.41/month (approximately A$120/month) before tax and additional variable usage, the owner stated: “We will accept this budget. Steps may be taken later to reduce costs.”

Accept the revised whole-portfolio planning budget, including existing hosting on B1, one APIM Developer unit, planned ACR Basic and Free App Configuration stores, with usage-dependent Key Vault/telemetry/network charges as disclosed. The former A$80 preference is superseded as the current budget baseline. This is a total hosting estimate, not A$120 of additional spend, a guaranteed invoice or a hard spending cap. Cost optimisation may be considered later without silently removing educational capabilities or weakening accepted controls.

Budget acceptance closes the presented cost decision. Resource topology/permissions and applicable exact platform deployment/what-if approval remain separate; no cloud changes are initiated by this record. Store isolation under ADR-031 and retention reduction are not implicitly accepted.

## Subsequent direction: include APIM Developer for education

Evidence: the human owner stated “Include the APIM Development resource. It is required for educational purposes. Re-calculate monthly hosting cost.” In context this means the previously proposed classic APIM Developer tier.

Include one shared APIM Developer unit in the development plan, retain B1 and defer PostgreSQL. This supersedes the APIM withdrawal in the earlier budget discussion below. The [updated budget](../infrastructure/development-hosting-budget-2026-10-30.md) estimates A$118.41/month before tax and incremental variable usage including planned ACR, or A$111.19 without ACR, based on a 730-hour month. No claim is made that the A$80 preference is achievable with this scope. This instruction authorises scope/cost recalculation, not a resource deployment or acceptance of unrelated store-isolation/retention changes.

## Owner-only educational Development hosting and portfolio cost target

Evidence: the human owner confirmed that Parameter Pilot, BlastIQ and Ticketing are for education/demonstration, with no users other than the owner while developing/testing; stated a desire to keep total hosting below $80 if possible; and directed keeping the App Service Plan at B1.

Recorded direction: retain shared B1/one worker, prioritise minimum required Development dependencies and use a below-A$80/month whole-portfolio planning target. AUD/month is the working interpretation of the conversation and Azure billing currency, not a separately confirmed hard cap. The prior B2 recommendation and A$120 incremental planning allowance are withdrawn. APIM Developer is withdrawn from the recommendation because its fixed cost does not fit that direction.

The [budget revision](../infrastructure/development-hosting-budget-2026-10-30.md) records actual-cost limitations and the next low-cost ingress assessment. This direction does not approve APIM Consumption, certificate-based ingress, ADR-031 store separation, deployment/spend, app shutdowns, shared-policy changes or merge. Preserve accepted security/ownership rules and raise material design conflicts. No Azure or platform-source changes occurred.
