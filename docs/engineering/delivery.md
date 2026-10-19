# CI/CD architecture

Version: 0.1 | Date: 8 October 2026 | Status: Proposed

Issue -> branch -> scoped change -> checks -> PR -> human approval -> merge -> immutable artefact -> environment approval -> deployment.

GitHub Actions is the intended baseline. Existing Azure DevOps pipelines remain observed assets; migrate deliberately and select one deployment authority. Do not silently remove current definitions or run competing deployers.

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
