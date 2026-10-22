# Definition of Done

Version: 0.2 | Date: 20 October 2026 | Status: Proposed

## Design

- Required areas covered; terminology/ownership/contracts/diagrams consistent.
- Confirmed direction separated from proposals; measurable targets or explicit TBDs.
- Decision/risk owners and readiness gaps visible.
- No fabricated implementation/deployment/approval.
- Full executable contracts/configuration validated before their implementation slice.
- Human acceptance evidence recorded for approved baseline.

## Implementation

- Approved requirements/criteria/design linked; scope/boundaries preserved.
- Relevant build/static checks and meaningful behavioural verification pass.
- Failed/skipped/unavailable checks reported honestly.
- Compatibility, migrations, security/entitlements/isolation reviewed.
- Appropriate telemetry, failure/recovery and privacy controls.
- Contracts/docs/traceability updated.
- PR evidence complete; required CI/specialist reviews and human approval before merge.

Apply checks proportionately: docs-only work needs document checks, not production tests. Ready for review, approved, merged and deployed are distinct states. Agent review cannot substitute for human approval.

## Accepted verification baseline

Apply [ADR-030](../architecture/decisions/adr-030.md) and the [testing strategy](testing-strategy.md): applicable checks pass before merge, failures block merge, skipped/unavailable evidence is reported, and no blanket coverage percentage substitutes for behaviour verification. Browser tests use controlled accounts/synthetic data and protected artefacts.
