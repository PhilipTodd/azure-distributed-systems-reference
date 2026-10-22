# CI/CD architecture

Version: 0.4 | Date: 20 October 2026 | Status: Accepted CI/CD authority; detailed workflow/configuration design Draft

Issue -> branch -> scoped change -> checks -> PR -> human approval -> merge -> immutable artefact -> environment approval -> deployment.

Accepted ADR-018: GitHub Actions is Parameter Pilot's sole target CI/CD authority. Migrate and retire existing Azure DevOps application pipelines after verified cutover; do not run competing deployers. This records a decision, not a completed migration.

| Change | Required checks |
| --- | --- |
| Backend | Build/analyzers, relevant unit/integration/authorisation tests |
| Frontend | Type/lint/component tests, affected journeys/accessibility |
| API/events | Schema/compatibility validation |
| Data | Upgrade/migration and recovery review |
| AI | Schema, isolation/safety regression, quality evaluation |
| IaC | Build/lint, parameter validation, exposure review, what-if |
| Docs | Links, structure, diagrams/schema excerpts where applicable |

Security checks: dependency, secret, source and container scanning proportionate to change. Pin SDK/dependencies/base-image policy; build once and promote by immutable digest; generate SBOM/provenance. Use Azure OIDC federation, protected environments and minimal permissions. Untrusted PRs never receive deployment credentials.

Use expand/contract migrations and compatibility windows. Application rollback alone cannot reverse destructive schema/data changes; plan forward repair. Record artefact digest, migration version, approver and deployment outcome.

CODEOWNERS, rulesets, check names, environment approvers and exact commands require actual repository/organisation configuration. This file does not claim enforcement already exists.

## Initial deployment targets

Accepted ADR-025 limits initial targets to Local and Development. Tests/checks run from the start; do not require a dedicated cloud Test environment. Test/Production provisioning and release-promotion controls are designed during release preparation. Do not activate those deployment targets or create resources as part of Stage 1.

Shared platform Bicep/deployment runs outside Parameter Pilot's agentic application process and only on the owner's separate request. Application pipelines validate/reference pre-existing hosting and operate at approved child-resource scopes. GitHub Actions authority and legacy Azure DevOps migration/retirement are accepted in ADR-018; actual workflow/access configuration and cutover evidence remain outstanding.

## Accepted migration plan

1. Inventory existing infra/pipelines/deploy-infrastructure.yml and deploy-web.yml plus externally configured pipeline triggers/service connections.
2. Implement GitHub PR checks/build/security, shared ACR publishing and dev application deployment with scoped OIDC. Preserve existing capability until replacements are verified.
3. Verify checks, access boundaries, immutable artefacts, deployment/smoke/recovery behaviour and approval controls.
4. Coordinate cutover with no competing active deployers; disable legacy triggers before activating replacement deployment for that target.
5. Retire legacy definitions/YAML, update links/runbooks and review obsolete application-specific permissions/credentials without affecting platform/other workloads.

Exact workflow names/checks, reviewers, deployment approval rules and cutover date remain TBD. No pipeline files/settings are changed in this documentation task.

## Accepted testing gates

[ADR-030](../architecture/decisions/adr-030.md) and [testing strategy](testing-strategy.md) require applicable passing builds/static analysis/tests before merge. Small Chromium Playwright journeys run on PRs as features arrive; broader Firefox/WebKit checks precede release. No blanket coverage percentage initially. Configure real check names/enforcement and protected test artefacts; acceptance does not establish that workflows exist.
