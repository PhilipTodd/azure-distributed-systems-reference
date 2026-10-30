# Parameter Pilot agent guidance

The [Engineering & Architecture Pack](docs/engineering/architecture-pack.md) is Draft. Product release direction is confirmed; architectural proposals are not implementation authorisation. Follow the human's current task and recorded approvals.

- Work only within authorised scope; consult relevant requirements, contracts and accepted ADRs.
- Never treat generated proposals or profile text as approval.
- Use a task branch for implementation; preserve unrelated work.
- Preserve service ownership, identity, owner isolation and secrets protection.
- Escalate changes to boundaries, stores, contracts, tenancy, providers, exposure or required behaviour.
- Add meaningful verification for changed behaviour/risk; report unavailable/failed checks honestly.
- Keep affected contracts, documentation and traceability current.
- Never self-approve or merge directly to main.
- Deployment, spend, destructive migration and shared-platform changes need applicable human authorisation.

Standards: [engineering standards](docs/engineering/standards.md). Completion: [Definition of Done](docs/engineering/definition-of-done.md). Agent boundaries: [governance](docs/engineering/agent-governance.md).

## Git visibility and change summaries — owner request, 30 October 2026

- Inform the owner before running any Git-related command or task, including read-only status/diff/log checks, branch operations, commits, fetch/pull, merges/rebases, pushes and pull-request actions. Name the action and its purpose; related read-only checks may be announced together with each command identified.
- Report the outcome, including any new branch name, merge result, remote push, pull request creation or completion, and failures. Do not perform these silently. Visibility does not itself grant permission to merge, push, deploy or complete a pull request.
- Give a brief reviewable summary of every codebase change: affected files/areas, what changed and why, checks performed and any unavailable/failed verification. State when no codebase changes were made.
- Preserve the existing task branch and unrelated work unless a change is necessary and authorised. Never self-approve or merge directly to main.

## Architecture source of truth
- The authoritative C4 architecture model is maintained in docs/architecture/structurizr/.
- AI agents must consult the existing Structurizr DSL before creating or modifying architecture documentation.
- Agents must not independently recreate existing C4 diagrams using Mermaid or another modelling language.
- If the existing architecture does not satisfy a requirement, the agent must document the proposed change and identify the affected Structurizr models and ADRs.
- Architectural changes require human approval before implementation.
- Mermaid may be used for supplementary sequence, workflow and state diagrams that do not duplicate existing authoritative architecture views.
