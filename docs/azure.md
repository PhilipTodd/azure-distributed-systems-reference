---
layout: page
title: Azure resources
eyebrow: Infrastructure
description: Azure infrastructure is managed by IaC (Infrastructure as Code). Bicep files defined in the infra/bicep folder manage Parameter Pilot specifc resources. Resources on the Shared Development Platform are referenced when necessary.
permalink: /azure/
---

`main.bicep` creates the application resource group for this project and the modules below. It also declares the Shared Development Platform resources as `existing` and wires their names, IDs, and connection strings into those modules. In this way the bicep files in this proejct are responsible for the resources "owned" by this project only while deploying to resources owned by the Shared Development Platform.

## Managed by this project

These resources are implemented in `infra/bicep` and live in `rg-distributed-systems-dev`, except the Cosmos container and Service Bus topic, which are created on the shared account and namespace in `rg-platform-dev`.

{% include azure-table.html %}

{% include callout.html type="info" title="No click-ops" content="Tiers in this table must match the IaC parameters. If a SKU changes, change the Bicep or Terraform first, then this table." %}

## Referenced from the shared platform

Declared as `existing` in `environments/dev/main.bicep`. This project consumes them. It does not create or set their SKUs.

{% include azure-table.html group="referenced" note="Referenced as existing resources in environments/dev/main.bicep. This project does not create them." %}
