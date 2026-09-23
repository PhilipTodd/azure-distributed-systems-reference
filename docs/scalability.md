---
layout: page
title: Scalability
eyebrow: Growth
description: Known limits, the first bottlenecks, and the plan before traffic is real.
permalink: /scalability/
---

This page is a forecast, not a load-test report. Be explicit about what has been measured and what has not.

## Concerns

| Area | Likely first limit | Plan |
| --- | --- | --- |
| App Service | CPU / instance count on B1 | Scale out, then a higher SKU |
| Data | DTU / connection pool on Basic SQL | Indexing, then a reserved SKU |
| Auth | Chatty login or session store | Cache identity, avoid per-request secrets |
| Chatty I/O | Unbounded lists or N+1 queries | Pagination and query budgets |

## What is not claimed

No published numbers live in this template. When a project site is filled, add the highest concurrent users tested (even if that number is small) and the hosting SKU used for that test.

{% include callout.html type="info" title="Honesty over theatre" content="A senior review reads this page for judgment. A missing number with a date to measure it beats an invented capacity story." %}
