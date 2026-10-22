# Initial environments and shared-platform prerequisite

Version: 0.3 | Date: 20 October 2026 | Status: Accepted environment scope; implementation details Draft

## Initial environment scope

| Environment | Purpose | Initial status |
| --- | --- | --- |
| Local | Developer execution and repeatable automated tests; compatible emulators/test doubles and selected authorised development Azure dependencies | Included initially |
| Development (dev) | Deployed integration tests and demonstrations on the shared Azure platform | Included initially |
| Test | Release validation environment to be designed during release preparation | Provisioning deferred |
| Production | Public operation, with release-specific identity/data/security/recovery controls | Provisioning deferred |

Acceptance: owner's explicit agreement to Local and Development only, with Test and Production provisioning deferred until release preparation; see ADR-025. Automated unit/integration/E2E tests still run initially. “Test environment deferred” does not mean testing deferred.

Use synthetic development data and development identities separate from eventual production. Local code may access approved dev dependencies where emulation is unsuitable; this is not a separate local Azure environment or permission to use production resources.

Exact versions, emulator feature coverage, runtime settings, network topology, deployment credentials and dev identities remain detailed decisions. No Test/Production resources, parameter files or deployment jobs are required merely to complete Stage 1.

## External platform prerequisite

The owner will separately request changes to azure-reference-platform and its Bicep deployment outside Parameter Pilot's agentic application development process. Shared development resources must be provisioned and verified before Parameter Pilot agentic implementation begins.

Platform infrastructure includes intended shared APIM, ACR, Key Vault, App Configuration, Blob Storage account and PostgreSQL Flexible Server, alongside existing shared SQL/Cosmos/Service Bus/compute/monitoring. This is an agreed target, not evidence they exist or permission to provision now.

Parameter Pilot references existing hosting and manages only approved application resources/content: API definitions/policies, images, scoped secrets/configuration, photo containers/lifecycle and Advisor database/schema/tables/embeddings. Shared PostgreSQL server/capacity/extensions/backups belong to the platform; Advisor owns its database and data.

Do not use naming prefixes or App Configuration labels as security boundaries. Verify enforceable isolation; use separate instances if the chosen shared arrangement cannot meet access requirements.

## Stage 1 readiness evidence

Before implementation, obtain platform deployment revision/resource IDs, endpoint/configuration references, approved child-resource management scopes, data-plane roles and sufficient capacity. Verify shared-plan compatibility/Always On, runtime access and local setup. Record how secrets are supplied without committing values.

The platform handover and verification are dependencies, not tasks authorising Parameter Pilot agents to modify or deploy the platform. APIs/workers/AI/photo features still arrive in their delivery stages; platform readiness does not require unused application workloads to be deployed.

## Release preparation

Before the first public release, explicitly decide Test/Production provisioning, physical/logical isolation, costs, identity/data separation, access, deployment/promotion approvals and recovery. Production suitability is not inferred from successful dev demonstrations.

## Accepted Development hosting and configuration

ADR-011/026/027 define separate shared-plan API apps, conditional narrow public backend restrictions behind APIM, no initial Front Door/WAF, and App Configuration/Key Vault with managed identities. Local defaults may be committed only if nonsecret; local secrets use User Secrets/equivalent untracked settings. Individual developer identities and operational policies are now accepted; exact grants/bootstrap/retry/provider details remain to be specified; do not assume the documents create cloud resources.

## Accepted hybrid/developer baseline

ADR-029 selects hybrid Local execution: practical local stores/emulators and deterministic doubles, selected approved dev Azure dependencies and real-Azure feature checks. Developers use individual Entra identities/approved logins and scoped dev grants, distinct from customer sign-in. No copied deployed credentials/shared account. See [Local specification](local-development.md) and [technology baseline](../engineering/technology-baseline.md).

Configuration high-level refresh/rotation/failure policies are now accepted ADR-027; exact roles/bootstrap/retry/provider settings remain open.
