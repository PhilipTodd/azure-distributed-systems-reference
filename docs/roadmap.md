---
layout: page
title: Roadmap
eyebrow: Next
description: Proposed enhancements in Now / Next / Later. This is intent, not a contract.
permalink: /roadmap/
---

<ol class="pipeline">
  {% for item in site.data.roadmap.items %}
    <li class="pipeline__stage">
      <span class="pipeline__index">{{ forloop.index }}</span>
      <span class="pipeline__name">{{ item.title }}</span>
      <span class="pipeline__detail">{{ item.status | capitalize }} - {{ item.detail }}</span>
    </li>
  {% endfor %}
</ol>

Edit `_data/roadmap.yml` per project. Prefer a few committed items over a catalogue of ideas.

{% include callout.html type="note" title="Keep it short" content="If an item needs architecture, write an ADR and link it. The roadmap is not a second design spec." %}
