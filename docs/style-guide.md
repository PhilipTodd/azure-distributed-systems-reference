---
layout: page
title: Style guide
eyebrow: Template
description: Look and feel for every documentation site that clones this skeleton - navigation, type, callouts, panels, tabs, and buttons.
permalink: /style-guide/
---

This page is the visual contract. Accept the skeleton here, then fill project sites from the same layouts, tokens, and includes.

## Navigation and chrome

The **header** stays dark navy with a persistent Azure **Live demo** button. Inner pages use the **sidebar** for the full documentation map. The **footer** repeats demo, source, and issues so a reader never hunts for an exit to the running app.

{% include callout.html type="info" title="Per-project chrome" content="`_config.yml` project settings drive the name, pitch, demo URL, credentials, GitHub links, and hero image paths. Do not fork CSS to rebrand a single project." %}

## Type

Three families, used the same way on every site.

<div class="font-sample font-sample--display">Outfit - headings, buttons, labels</div>
<div class="font-sample font-sample--body">Source Sans 3 - body copy. Keep paragraphs short. Hiring managers skim.</div>
<div class="font-sample font-sample--mono">IBM Plex Mono - credentials, IaC paths, commands</div>

## Buttons

<div class="btn-row">
  <a class="btn btn--primary" href="{{ site.project.demo.url }}" target="_blank" rel="noopener noreferrer">Live demo</a>
  <a class="btn btn--secondary" href="{{ site.project.github.repo }}">Source</a>
  <a class="btn btn--ghost" href="{{ '/architecture/' | relative_url }}">Architecture</a>
  <button class="btn btn--danger" type="button">Destructive</button>
  <button class="btn btn--tiny" type="button">Copy</button>
</div>

The primary button is Azure Blue (`#0078D4`) at high contrast on both the dark header and the light page.

## Callouts

{% include callout.html type="info" title="Info" content="Use for facts a reviewer should not miss: demo URL caveats, diagram source, IaC path." %}
{% include callout.html type="success" title="Success" content="Use for an accepted decision, a passing gate, or a production control that is already in place." %}
{% include callout.html type="warning" title="Warning" content="Use for staging-only credentials, incomplete ADRs, or known scale limits." %}
{% include callout.html type="danger" title="Danger" content="Use for outage, data-loss, or security constraints." %}
{% include callout.html type="note" title="Note" content="Use for template guidance that should disappear from a finished project site." %}

## Panels

<div class="panel-grid">
  <div class="panel">
    <div class="panel__header">
      <h3 class="panel__title">Golden signals</h3>
      <span class="panel__meta">App Insights</span>
    </div>
    <div class="panel__body">
      <p>Latency, errors, traffic, saturation. One panel per signal on the operations page.</p>
    </div>
  </div>
  <div class="panel">
    <div class="panel__header">
      <h3 class="panel__title">Rollback</h3>
      <span class="panel__meta">Slot swap</span>
    </div>
    <div class="panel__body">
      <p>Previous slot remains warm. Swap back is the default rollback, not a forward deploy.</p>
    </div>
  </div>
</div>

## Tabs

Used on Architecture for C4 levels. Keyboard: Left/Right, Home/End.

<div class="tabs" data-tabs>
  <div class="tabs__list" role="tablist" aria-label="Component demo">
    <button class="tabs__tab" type="button" role="tab" id="tab-demo-1" aria-controls="panel-demo-1" aria-selected="true">System Context</button>
    <button class="tabs__tab" type="button" role="tab" id="tab-demo-2" aria-controls="panel-demo-2" aria-selected="false" tabindex="-1">Container</button>
    <button class="tabs__tab" type="button" role="tab" id="tab-demo-3" aria-controls="panel-demo-3" aria-selected="false" tabindex="-1">Component</button>
  </div>
  <div class="tabs__panel" role="tabpanel" id="panel-demo-1" aria-labelledby="tab-demo-1">
    <p>People and systems around the application. Export from Structurizr into <code>assets/diagrams/c4-context.svg</code>.</p>
  </div>
  <div class="tabs__panel" role="tabpanel" id="panel-demo-2" aria-labelledby="tab-demo-2" hidden>
    <p>Deployable units and data stores. Export into <code>assets/diagrams/c4-container.svg</code>.</p>
  </div>
  <div class="tabs__panel" role="tabpanel" id="panel-demo-3" aria-labelledby="tab-demo-3" hidden>
    <p>Components inside the primary container. Export into <code>assets/diagrams/c4-component.svg</code>.</p>
  </div>
</div>

## Status badges and decision log

{% include adr-log.html %}

## Pipeline

{% include pipeline.html %}

## Azure resource table

{% include azure-table.html %}

## Hero images

Supply both orientations on each project build. The home page picks landscape from 720px up and portrait below that.

| Orientation | Size | Config key |
| --- | --- | --- |
| Landscape | 1700 x 900 | `project.images.landscape` |
| Portrait | 900 x 1700 | `project.images.portrait` |
