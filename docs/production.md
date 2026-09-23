---
layout: page
title: Production readiness
eyebrow: Operations
description: Disaster recovery, downtime communications, rollback, observation, and alerting - the gap between a demo and a service.
permalink: /production/
---

The live demo is not production. This page is the list of work that remains before treating the system as a service.

## Disaster recovery

- Recovery point and recovery time objectives are not yet set for this template.
- State whether the data store uses geo-redundant backups, and where the runbook lives.
- Name the restore drill cadence once the project exists.

## App downtime communications

- Who notices first: alert, user report, or pipeline failure.
- Status note location (README, status page, or issue template).
- Audience: demo users versus a real customer list.

## Rollback

- Default: swap back to the previous App Service slot / last known good artifact.
- Forward-fix only when rollback would lose data that cannot be restored.
- Record the command or pipeline job that performs the rollback.

## Observation and alerting

See [Observability]({{ '/observability/' | relative_url }}). Production additionally requires:

- An action group that reaches a human.
- Alerts on error burn, dependency failures, and saturation - not CPU graphs without a threshold.
- A quiet-hours policy for a demo tenant, and a stricter one if the app is ever customer-facing.

{% include callout.html type="warning" title="Template status" content="Replace each bullet with the project's actual control, or mark it explicitly as not in place. Do not imply production maturity the demo does not have." %}
