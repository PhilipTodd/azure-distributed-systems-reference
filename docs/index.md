---
layout: home
title: Overview
description: Pitch, live demo, and credentials for this reference project.
hide_sidebar: true
permalink: /
---

{% include callout.html type="note" title="Project under development" content="This application is in primary development stage. These docs represent proposed standards and practices used during implementation as well as design choices.

Although I will endevour to update docs as I go - the actual implentation may vary from content on these pages" %}

## Product purpose

Aquarium owners record water chemistry, livestock/tank information and maintenance history and receive useful analysis and AI-assisted recommendations.

## Engineering purpose

This reference application is intended to demonstrate:
* distributed system design 
* microservices 
* asynchronous/event-driven architecture 
* REST APIs 
* API management 
* authentication/authorization 
* SaaS subscription management 
* containerisation 
* relational and NoSQL persistence 
* blob/object storage 
* serverless processing 
* AI integration 
* RAG/vector search 
* observability/distributed tracing 
* resilience 
* IaC 
* CI/CD 
* external integrations 


<ul class="jump-cards">
  <li>
    <a href="{{ '/architecture/' | relative_url }}">
      <strong>Architecture</strong>
      <span>C4 context, container, and component views from Structurizr.</span>
    </a>
  </li>
  <li>
    <a href="{{ '/decisions/' | relative_url }}">
      <strong>Decision log</strong>
      <span>ADRs in Date | Status | Title format.</span>
    </a>
  </li>
  <li>
    <a href="{{ '/deployment/' | relative_url }}">
      <strong>Deployment pipeline</strong>
      <span>Linting through production, including the gated release.</span>
    </a>
  </li>
  <li>
    <a href="{{ '/production/' | relative_url }}">
      <strong>Production readiness</strong>
      <span>Rollback, communications, disaster recovery, and alerting.</span>
    </a>
  </li>
</ul>

