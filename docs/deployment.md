---
layout: page
title: Deployment pipeline
eyebrow: Delivery
description: GitHub Actions is the sole Parameter Pilot CI/CD authority; migrate and retire Azure DevOps after verified cutover.
permalink: /deployment/
---

## Delivery authority

Accepted [ADR-018](architecture/decisions/adr-018.md): GitHub Actions is the sole target for Parameter Pilot CI/CD. Existing infra/pipelines Azure DevOps definitions are legacy migration inputs, not a second intended authority. They have not been retired by this documentation update.

## Intended checks and deployment

| Step | Intended gate |
| --- | --- |
| Pull request | Applicable build, formatting/static, meaningful tests and security checks |
| Merge | Required checks/reviews and human approval |
| Artefact | Build/publish approved images to shared ACR; immutable release identity |
| Development deployment | Scoped Azure OIDC, applicable authorisation and smoke/recovery verification |
| Release preparation | Decide Test/Production topology/provisioning and promotion controls separately |

Initially establish Local/dev only (ADR-025). Automated tests start immediately; no dedicated Test environment is required. Exact workflow/check names and branch/environment protections must be configured and verified.

## Legacy migration

Verify replacement capabilities, coordinate cutover without competing active deployers, then retire Azure DevOps triggers/definitions/YAML and obsolete app-specific credentials after dependency review. See [delivery design](engineering/delivery.md).

Shared platform provisioning/deployment is independently managed and occurs only on the owner's separate request. Parameter Pilot deploys approved app resources against pre-existing platform hosting. This page does not establish any workflow or deployment currently runs.
