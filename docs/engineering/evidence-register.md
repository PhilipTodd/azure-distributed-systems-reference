# Evidence register

Version: 0.2 | Date: 19 October 2026 | Status: Draft

## Status vocabulary

| Status | Meaning |
| --- | --- |
| Confirmed intent | Owner direction carried forward from the handover or current chat |
| Observed | File content inspected; not proof of deployment or behaviour |
| Proposed | Recommendation awaiting human approval |
| TBD | Missing or unresolved information |

## Sources

Primary handover: `C:\AI-Context\context-azure-distributed-systems-reference\Parameter-Pilot-Engineering-Architecture-Pack-Handoff.md`, prepared 7 October 2026. It cites the earlier “Choose Parameter Pilot” conversation. That conversation was not independently retrieved for this pack.

The current checkout was inspected rather than assuming the handover's selective Repomix snapshot describes present implementation. The snapshot was not modified and was not required to establish the observations below.

| Evidence | Observation | Limit |
| --- | --- | --- |
| `ParameterPilot.slnx` | Folder entries and legacy OrderService name; no project entries | No functioning application solution established |
| `src/web/coming-soon` | Static page and image | Not the proposed Angular application |
| `docs/architecture/structurizr` | Parameter Pilot candidates for three services and a generic event processor | Not accepted service boundaries |
| `infra/bicep/main.bicep` | Resource group and Static Web App module | No broader platform wiring established |
| `infra/pipelines` | Azure DevOps deployment YAML | Conflicts with intended GitHub Actions delivery authority |
| `docs/azure.md` | Claims shared-resource wiring and broad application resources | Claims exceed inspected Bicep |
| `README.md` | Legacy reference-project branding | Must be reconciled deliberately |
| Jekyll configuration and documentation | Existing presentation system | Preserve until a presentation change is approved |

## Reconciliation backlog (initial 8 October inventory; see update below)

- Add explicit Foundry inference dependency to Structurizr.
- Replace unrestricted cross-service store access with owner APIs or approved projections.
- Replace generic event-processor ownership with service-owned worker roles.
- Rename “Parameter Event Store” to Tracking History Store; no full event sourcing is proposed.
- Replace ambiguous PhotoUploaded/PhotoAdded terminology with distinct upload/processing states.
- Model SPA token acquisition separately from gateway validation.
- Reconcile legacy OrderService and project branding.
- Correct infrastructure documentation when modules actually exist.
- Select one CI/CD authority before migrating deployment pipelines.

No live Azure resources, permissions, domain ownership, budgets or running services were verified. No application build/test result is implied by this pack.

## Model update — 19 October 2026

Initial observations above describe the pre-update evidence. The authorised decision record now selects PostgreSQL/pgvector and Tracking photo uploads/worker derivatives; canonical DSL is updated for those changes and Advice history. See [current C4 reconciliation](../architecture/c4.md) and [approval record](authorised-decisions-2026-10-19.md). Duplicate Mermaid C4 views were removed. Generated workspace.json/SVGs remain stale until regenerated; other model gaps remain open. No live Azure verification or deployment is implied.
