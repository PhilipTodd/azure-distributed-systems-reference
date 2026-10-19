# AI architecture and evaluation

Version: 0.2 | Date: 19 October 2026 | Status: Proposed; later-release capability

Pipeline: authorise -> reserve quota -> capture context -> retrieve references -> infer -> validate -> persist -> present.

## Context and knowledge

Context includes authorised profile/owner context, readings with units/qualifiers/age, maintenance/dosing/observations, test-method changes, gaps/conflicts and source revisions. Capture collection interval and source versions; API calls across services do not create an atomic global snapshot. Disclose material inconsistencies.

Private history stays structured, accessed through owner APIs. Curated reference passages, metadata and embeddings are stored in Advisor-owned PostgreSQL and retrieved with pgvector, replacing the proposed AI Search component. Each source records publisher/title/URL, rights/licence, subject scope, content version, review date and reviewer. Only approved material enters the production index.

User notes and retrieved content are untrusted data. They cannot override instructions, request secrets or authorise tools. Initial advisor has no mutation tools.

## Output shape

```json
{
  "requestId": "uuid",
  "status": "completed",
  "summary": "Plain-language assessment",
  "dataQuality": {"missing": [], "stale": [], "contradictions": []},
  "recommendations": [{
    "action": "Suggested owner action",
    "rationale": "Grounded explanation",
    "urgency": "routine",
    "evidenceIds": ["measurement:panel-id:revision"],
    "citationIds": ["source-id:version:chunk-id"]
  }],
  "uncertainties": [],
  "limitations": [],
  "provenance": {
    "contextVersion": "context-v1",
    "promptVersion": "advisor-v1",
    "knowledgeVersion": "corpus-version",
    "modelDeploymentVersion": "approved-version"
  }
}
```

This illustrative shape needs a full bounded schema and urgency vocabulary. Evidence/citation IDs must resolve to actual supplied context/retrieval, not model-created sources.

## Behaviour and failure policy

- Never fabricate readings, citations, precision or certainty.
- Missing essential inputs produce clarification or abstention.
- Numeric dosing requires approved calculator provenance; otherwise abstain.
- Photos are excluded from AI context throughout this pack: no image binaries, image URLs or image embeddings. No physical control.
- Persist recoverable job failure on model/PostgreSQL retrieval outage; tracking remains usable.
- Reserve quotas atomically; settle/release under approved customer policy.
- Check access during work and before returning protected results.
- Bound tokens, job concurrency, retry and spend; model timeout may still incur cost.
- Keep raw prompts/private notes out of routine telemetry.

## Evaluation gates

| Case | Expected result |
| --- | --- |
| Sparse/stale history | Disclose limitations and ask for useful missing data |
| Incompatible units | Refuse unsupported comparison |
| Contradictory data | Identify conflict |
| Note/retrieval injection | Ignore unauthorised instructions |
| Cross-owner IDs | No retrieval or disclosure |
| Unsupported citation | Validation failure or abstention |
| Missing dosing concentration | No invented dose |
| Provider outage | Recoverable terminal status |

All release-blocking safety/isolation cases pass; proposed usefulness threshold >=80%. Record dataset/rubric, reviewer and model/prompt/context/corpus versions. Changes trigger proportionate regression evaluations and rollback review. Evaluation data must be synthetic or explicitly approved/redacted.

Exact model/region/version, quota, provider data handling, per-job cost and knowledge corpus remain approval blockers.

## Accepted history and persistence decisions

The Advice page presents a scrollable, paginated history list. Selecting an item shows advice and the immutable parameter values actually submitted with that AI request, with units and measured times. Store that snapshot in PostgreSQL with the job/result and access checks; do not reconstruct it from amended live readings. Conversational threading is not included.

One Advisor PostgreSQL instance stores relational jobs/results/quotas/snapshots and curated reference passages/metadata/pgvector embeddings. No separate Advisor SQL or Azure AI Search deployment is required. Validate index/metadata-filter behaviour, recall, latency, pooling and cost before release. Retained original photos are not available to Advisor as context.

Add evaluations for history snapshot fidelity after source corrections, cross-owner history access, pagination and exclusion of photo content. See [authorisation record](../engineering/authorised-decisions-2026-10-19.md).
