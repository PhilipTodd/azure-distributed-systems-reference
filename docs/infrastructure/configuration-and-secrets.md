# Configuration and secrets

Version: 0.3 | Date: 20 October 2026 | Status: Accepted storage/access arrangement; detailed policies Draft

| Information | Accepted location |
| --- | --- |
| Deployed nonsecret settings / feature flags | Shared Azure App Configuration |
| Unavoidable secrets | Shared Key Vault |
| Secret pointers | Key Vault references where supported; no secret value in App Configuration |
| Local nonsecret defaults | Version-controlled configuration |
| Local dev secrets | .NET User Secrets or equivalent untracked local settings |
| Browser configuration | Public/nonsecret values only |

Managed identities are the preferred deployed access mechanism. Each API/worker receives only the required content access. Local User Secrets is unencrypted; protect developer accounts/machines and never use it as production vault hosting.

Platform owns shared service lifecycle/security; app owns its scoped content/approved assignments. Verify actual enforceable separation; labels/prefixes do not restrict access. Separate instances require appropriate owner/platform approval where shared isolation is insufficient.

Still decide naming, concrete RBAC/developer grants, bootstrap/precedence, retry/timeouts, secret version selection/provider rotation details and audit implementation. Startup/restart refresh, operator-controlled rotation and required-configuration failure policy are accepted below; no numeric periods or actual credentials are set here.

Acceptance tests: allowed access succeeds; cross-app access denied; no source/browser/log/image artefact secret leakage; setup reproducible; later refresh/rotation/failure policies demonstrable.

See accepted [ADR-027](../architecture/decisions/adr-027.md), [environment scope](../development/environments.md) and [security](../architecture/security.md).

[Key Vault references](https://learn.microsoft.com/azure/azure-app-configuration/use-key-vault-references-dotnet-core), [local secrets](https://learn.microsoft.com/en-us/aspnet/core/security/app-secrets?view=aspnetcore-10.0), [App Service access restrictions](https://learn.microsoft.com/en-us/azure/app-service/overview-access-restrictions).

## Accepted service access matrix

| Identity | Permitted access | Not implied |
| --- | --- | --- |
| Aquarium API and Aquarium worker, each independently scoped | Required Aquarium settings and Aquarium secrets | Tracking/Advisor secrets or configuration administration |
| Tracking API and Tracking worker, each independently scoped | Required Tracking settings and Tracking secrets | Aquarium/Advisor secrets or configuration administration |
| Advisor API and Advisor worker, each independently scoped | Required Advisor settings and Advisor secrets | Aquarium/Tracking secrets or configuration administration |
| Application deployment identity | Approved configuration-management rights, separate from runtime grants | Blanket secret reads/administration, other-project or platform-wide rights |

Each API/worker keeps its own managed identity and only necessary grants, even within one service. Explicitly approved nonsecret settings may be shared; cross-service secret access is not automatic.

### Enforcement and readiness

Verify shared App Configuration/Key Vault support the exact intended boundaries using enforceable access controls. Names, key prefixes and labels merely organise data. If isolation cannot be enforced, propose separate stores/vaults for approval; do not broaden service access silently or provision replacements automatically.

Test required reads, denied cross-service reads, approved shared nonsecret access, denied runtime administration and bounded deployment management. Record evidence before Stage 1 access readiness is closed.

### Remaining decisions

Select actual roles/scopes, developer access, sharing rules and concrete implementation. High-level refresh/rotation/failure policies are now accepted below; exact implementation settings remain TBD. Service-level isolation is accepted; these unresolved settings do not revoke that acceptance. See ADR-027 for approval evidence.

## Accepted operational policy

| Situation | Accepted behaviour |
| --- | --- |
| Startup/config change | Load at startup; controlled restart/redeploy applies ordinary changes in initial dev |
| Feature flags | Dynamic refresh deferred until specific need |
| Running jobs | Keep starting configuration; interrupted work retries/resumes under idempotent job design |
| Secret rotation | Operator controlled; use provider-supported overlap, Key Vault update, affected-app restart and verification before old-secret revocation |
| No credential overlap | Coordinated maintenance; do not assume zero interruption |
| Suspected exposure | Prompt rotation/revocation handling |
| Key Vault update | Not proof of live connection renewal; verify actual downstream use |
| Missing/invalid required startup config/secret | Not Ready; no request/job processing; safe diagnostics, bounded retries |
| Configuration-store outage while running | Continue loaded settings only if required authorisation/downstream access still valid |
| Required credentials/authorisation fail | No insecure fallback; fail protected operation; recoverable job remains retryable, never false success |
| Local dev Azure identity | Individual Entra login with approved dev permissions; no shared account/copied workload identity |

Detailed retry limits, restart draining/resumption, actual role scopes, provider credential lifetimes/version selection and renewal/revocation mechanics remain open. No automatic scheduled rotation or continuous configuration refresh is introduced. See ADR-027/029 for authority.
