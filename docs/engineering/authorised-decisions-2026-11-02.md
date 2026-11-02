# Authorised decisions — 2 November 2026

## Deploy PP Development service foundations

Owner instruction: “I do not understand the differences. I suggest we go ahead and attempt to deploy the PP resources using bicep. If the coming-soon website is disrupted I am not concerned.” This followed explanation of the three website/domain Modify entries and authorisation/completion of the full Development preview.

Authorised scope: deploy the current PP Development main.bicep through its established environment entry point, with deployServiceFoundations=true for the deployment. Include the reviewed two stopped/closed API identity hosts, two Free App Configuration stores, two Standard RBAC Key Vaults with the proposed deletion protection, four read-role assignments and four publishing-policy children. The owner accepts applying the previewed existing website/domain differences, including possible disruption of the coming-soon site. This supersedes the requirement to resolve those differences before this deployment; it does not establish that the differences are harmless.

Preserve shared B1/platform resources, other products, service isolation and secret protection. Do not deploy feature code/images, start or expose APIs, grant broad access, create SQL/Cosmos users/containers or provision deferred workers. No Git commit/push/PR/merge is authorised by this deployment instruction. Actual deployment outcome and post-deployment checks must be recorded separately.

Outcome: deployment `pp-foundations-dev-20261102-1e43f0ac` Succeeded. Resource settings and scoped read-role assignments were verified; shared B1 and pre-existing applications matched snapshots, and the website/default and both custom domains returned HTTPS 200. Effective workload isolation and SQL/Cosmos access remain unverified. See [deployment evidence](../infrastructure/evidence/pp-foundations-deployment-2026-11-02.json).
