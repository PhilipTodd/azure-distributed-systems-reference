---
layout: page
title: Deployment pipeline
eyebrow: Delivery
description: Lint, unit tests, integration, staging, then production. Same sequence whether the host is GitHub Actions or Azure DevOps.
permalink: /deployment/
---

{% include pipeline.html %}

{% include callout.html type="info" title="Replace with the real workflow" content="Edit `_data/pipeline.yml` so stage names match the YAML in `.github/workflows` or the Azure DevOps pipeline. Link the workflow file from this page when the project site is filled." %}

## Gates

| Stage | Blocks promotion when |
| --- | --- |
| Linting | Format, analyzers, or policy checks fail |
| Unit tests | Coverage or failed assertions |
| Integration | Contract, API, or data tests fail |
| Staging | Smoke tests or a failed slot deploy |
| Production | Missing approval or a red staging gate |

## Live demo

The running environment is the outcome of this pipeline, not a sidecar.

<div class="btn-row">
  <a class="btn btn--primary" href="{{ site.project.demo.url }}" target="_blank" rel="noopener noreferrer">{{ site.project.demo.label }}</a>
</div>
