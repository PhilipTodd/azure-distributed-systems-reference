# Stage 1 readiness and agent guidance

Version: 0.1 | Date: 21 October 2026 | Status: Accepted preparation approach; completion evidence pending

This is the working companion to the public [delivery plan](delivery-plan.md). It consolidates current Stage 1 guidance formerly repeated beneath that page's change history. It does not authorise application implementation, deployment, spending, shared-platform changes or merge.

## Current completion path

No further high-level design Q&A is required before readiness preparation and read-only evidence gathering. Routine implementation details follow accepted design; escalate material changes to ownership, stores, security, contracts or behaviour. Selective acceptance does not approve unrelated Draft proposals.

1. Prepare the Stage 2 readiness specification: exact supported SDK/package/container versions, executable profile/tank/panel and Aquarium-validation schemas, scientific seed proposals with explicit units/basis/rules, configuration placeholders, Local instructions and platform/evidence checklist.
2. Validate compatibility and contracts. Present scientific seed definitions and the concrete baseline for human review. Make numeric precision, unit variants and request limits explicit; generated records are not approved merely because they exist.
3. Obtain platform handover for the required Aquarium/Tracking dependencies: actual resource IDs, runtime/plan compatibility, network feasibility, effective scoped permissions and configuration access. Repository definitions are not evidence of deployed resources.
4. Under applicable authorisation, establish and verify reproducible Local/dev bootstrap and proportionate baseline build/static/test/delivery checks. Report unavailable verification honestly. Feature tests arrive with their features.
5. Assemble completion evidence and scoped Stage 2 acceptance criteria for human review. Stage 1 acceptance and application-implementation authorisation remain distinct gates.

## Authoritative build inputs

| Area | Current guidance |
| --- | --- |
| Approvals and open risks | [21 October decisions](authorised-decisions-2026-10-21.md), [20 October decisions](authorised-decisions-2026-10-20.md), [decision register](decision-register.md), [ADR catalogue](../architecture/decisions/README.md) |
| Identity | [ADR-009](../architecture/decisions/adr-009.md): External ID, profile completion, per-service delegated permissions, tid + oid mapping, certificate-authenticated Tracking OBO, worker context/internal-operation boundaries |
| Tank/profile | [Contract](../api/tank-and-profile-contract.md): explicit measurement-system choice without a default, tank fields, quantity/unit preservation and future advice snapshots |
| Measurement panels | [ADR-023](../architecture/decisions/adr-023.md), [Aquarium validation contract](../api/aquarium-validation-contract.md), [Tracking API draft](../api/tracking-openapi-draft.md): selection/units/basis, panel limits, error/input preservation and validation-time consistency |
| Stores and async processing | [Data design](../architecture/data.md), [async design](../architecture/asynchronous-processing.md): service-owned stores, /tankId, local same-container/partition atomicity, outboxes and scoped messaging |
| Versions and Local setup | [Technology baseline](technology-baseline.md), [Local development](../development/local-development.md), [ADR-029](../architecture/decisions/adr-029.md): direct local UI/APIs, Compose SQL/Cosmos dependencies, real dev identity, synthetic seeds and cloud verification |
| Hosting/network/configuration | [Platform inventory](../infrastructure/platform-inventory.md), [dev API access](../infrastructure/development-api-access.md), [configuration/secrets](../infrastructure/configuration-and-secrets.md) |
| Checks and delivery | [Testing strategy](testing-strategy.md), [delivery](delivery.md), [standards](standards.md), [Definition of Done](definition-of-done.md), [agent governance](agent-governance.md) |
| Diagnostics | [Observability](../architecture/observability.md), [ADR-017](../architecture/decisions/adr-017.md), [runbooks](../operations/runbooks.md): accepted Local/dev baseline, retention/sampling, initial triggers and owner response |
| Architecture views | [Authoritative Structurizr source](../architecture/structurizr/workspace.dsl); do not duplicate C4 in Mermaid |

## Platform and sequencing boundaries

- Local and Development only initially. Verify owner-managed required platform additions before application implementation; platform changes/deployment remain outside the Parameter Pilot agentic process until separately requested.
- Verify shared Linux plan/runtime/Functions support, Always On where required, available capacity, APIM addressing/restrictions and enforced data/configuration isolation. Bring infeasibility back for a focused decision rather than weakening security.
- GitHub Actions is sole application CI/CD authority. Verify replacement workflows/scoped OIDC and safe noncompeting Azure DevOps retirement; shared-platform pipelines are separately managed.
- Preserve synchronous core writes and local transactional outbox semantics. Add broker relays/workers as their authorised slices require; do not invent delivery evidence or dummy workloads.
- Runtime and deployment permissions are separate. Actual identifiers, certificates, effective grants and notification destination are setup inputs, not more high-level product decisions.

## Deferred work

The reference project does not require the former 50-concurrent-owner/large seeded-data benchmark. The accepted 750 ms p95 API target guides implementation; it does not require a Stage 1 commercial-scale load test. Revisit commercial capacity when warranted.

Do not block Stage 2 on unused Advisor/PostgreSQL/photo dependencies, full later-stage recovery/cost tuning, advanced agent profiles or Test/Production provisioning. Public-release security/privacy/accessibility/recovery/support gates still apply at Stage 4. Customer MFA is reassessed at Stage 6, earlier if risks materially change. AI/commercial/image-encoding/dosing/Xero decisions remain with their stages.

## Evidence and approval status

The readiness specification and verified environment/check evidence remain outstanding. This document does not establish resources exist, tests passed or Stage 1 is complete. If compatibility, scientific review or platform verification reveals a material conflict, raise that specific decision before affected implementation.

Decision chronology remains in approval records and ADRs. Repeated historical summaries from the delivery page were removed rather than copied here; linked source documents retain the accepted rules.
