---
layout: page
title: Development
eyebrow: Source
description: Branching strategy, how to run the demo, and the current GitHub issues.
permalink: /development/
---

## Live demo

<div class="btn-row">
  <a class="btn btn--primary" href="{{ site.project.demo.url }}" target="_blank" rel="noopener noreferrer">{{ site.project.demo.label }}</a>
  <a class="btn btn--ghost" href="{{ site.project.github.issues }}" target="_blank" rel="noopener noreferrer">Current issues</a>
</div>

{% if site.project.credentials.enabled %}
{% include credentials.html %}
{% endif %}

## Instructions

1. Open the live demo with the button above.
2. Sign in with the credentials on this page when the app is behind a login.
3. Stay on the sample tenant. Do not upload real data.

## Branching

**GitHub Flow** is the default for this template: `main` is always releasable, changes land through short-lived pull requests, and the pipeline on `main` deploys.

Trunk-based development is an alternative if the application repo uses it - say so here and link the ADR. Do not mix unnamed branch models across the three reference projects unless an ADR explains why.

## Issues

Open work lives on GitHub, not in this site.

<a href="{{ site.project.github.issues }}" target="_blank" rel="noopener noreferrer">{{ site.project.github.issues }}</a>
