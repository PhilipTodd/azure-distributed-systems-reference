# Agent governance and specialist profiles

Version: 0.1 | Date: 8 October 2026 | Status: Draft

Root AGENTS.md is concise behaviour guidance; engineering standards contain detailed rules. Copilot-wide instructions link to sources, path instructions specialise them, and profiles describe scoped roles. All generated profiles remain Draft and do not approve implementation.

| Profile | Permitted task scope | Escalation |
| --- | --- | --- |
| Backend | Assigned service/tests | Boundary or contract redesign |
| Frontend | SPA/tests | API/UX requirement changes |
| Cloud | Assigned IaC/container/workflow assets | Shared platform/exposure/spend |
| AI | Advisor/prompts/evaluations | Model/provider or mutation tools |
| QA | Tests/fixtures | Defects requiring production changes |
| Reviewer | Review findings | No self-approval/merge |
| Writer | Docs/contracts/diagrams | Approved design meaning changes |
| Quality | Scoped quality config/formatting | Disabling gates/unrelated rewrites |
| Security | Review and explicitly assigned fixes | Architecture/exposure changes |
| Data, optional | Assigned persistence/migrations | Destructive change or ownership |

Every profile declares inputs, paths/tools, exclusions, dependencies, escalation, commands, PR evidence and completion. Exact commands wait for real projects. Coordinate overlapping edits explicitly. Data engineering can initially be a backend responsibility.

No tools are explicitly granted in the draft profiles. Omitted tool settings must not be interpreted as a restrictive sandbox; configure actual least-privilege tooling before use. Text guidance is not access control. Enforce with repository permissions, CODEOWNERS, rulesets, checks, secrets isolation and environments.

GitHub documents repository/path instructions and environment-specific custom-agent support. Validate target IDE/cloud discovery/frontmatter/tool names before adoption. [Repository instructions](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/add-custom-instructions/add-repository-instructions), [agent configuration](https://docs.github.com/en/copilot/reference/custom-agents-configuration).
