# Authorised decisions — 2 November 2026

## Deploy PP Development service foundations

Owner instruction: “I do not understand the differences. I suggest we go ahead and attempt to deploy the PP resources using bicep. If the coming-soon website is disrupted I am not concerned.” This followed explanation of the three website/domain Modify entries and authorisation/completion of the full Development preview.

Authorised scope: deploy the current PP Development main.bicep through its established environment entry point, with deployServiceFoundations=true for the deployment. Include the reviewed two stopped/closed API identity hosts, two Free App Configuration stores, two Standard RBAC Key Vaults with the proposed deletion protection, four read-role assignments and four publishing-policy children. The owner accepts applying the previewed existing website/domain differences, including possible disruption of the coming-soon site. This supersedes the requirement to resolve those differences before this deployment; it does not establish that the differences are harmless.

Preserve shared B1/platform resources, other products, service isolation and secret protection. Do not deploy feature code/images, start or expose APIs, grant broad access, create SQL/Cosmos users/containers or provision deferred workers. No Git commit/push/PR/merge is authorised by this deployment instruction. Actual deployment outcome and post-deployment checks must be recorded separately.

Outcome: deployment `pp-foundations-dev-20261102-1e43f0ac` Succeeded. Resource settings and scoped read-role assignments were verified; shared B1 and pre-existing applications matched snapshots, and the website/default and both custom domains returned HTTPS 200. Effective workload isolation and SQL/Cosmos access remain unverified. See [deployment evidence](../infrastructure/evidence/pp-foundations-deployment-2026-11-02.json).

## Stage 1 scoped SQL/Cosmos access

The owner instructed: “Proceed with step 1. Explain what is required and action if possible.” This followed the remaining Stage 1 item “Establish Aquarium SQL and Tracking Cosmos scoped access.” The owner separately selected “Use parameterpilot-tracking (Recommended)” when asked to approve that container in ReferenceProjects with /tankId and no dedicated throughput.

Authorised actions performed: create Aquarium’s isolated schema/security roles and a contained external user bound to the verified deployed API identity; verify permission boundaries with rolled-back synthetic probes; deploy the PP-owned parameterpilot-tracking container and its custom container-scoped data role through the existing PP main.bicep. No domain-table design, feature migration, runtime activation, broad grant or shared capacity change is authorised by this work. Migration role membership and production table grants remain unset.

Outcome: SQL bootstrap applied and rerun successfully. Transactional probe CRUD and 14 denial/membership checks passed; all probe tables and grants rolled back. Tracking deployment pp-tracking-access-20261102-b31e7904 Succeeded. Management inspection verified exact container scope and eight explicit metadata/CRUD/query/feed actions; BlastIQ container definition and shared 400 RU/s stayed unchanged. Actual managed-identity authentication/SDK isolation tests remain pending. See [scoped-access runbook](../infrastructure/scoped-data-access.md).
