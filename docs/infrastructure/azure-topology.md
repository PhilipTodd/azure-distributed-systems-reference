# Azure deployment and ownership

Version: 0.2 | Date: 19 October 2026 | Status: Proposed

Australia East is the accepted preference, subject to actual service/model availability. Budget remains unset; choose appropriate low-cost tiers. No SKU or provisioning approval is established.

| Resource | Purpose | Ownership proposal |
| --- | --- | --- |
| Static Web Apps | Angular assets | Application |
| Front Door/WAF | Proposed edge | Platform/application TBD |
| APIM | Gateway/policies | Shared platform if suitable |
| App Service | Containerised APIs | Application workloads on approved plan |
| Functions/worker hosting | Service-owned async jobs | Workload-specific |
| Azure SQL | Aquarium database | App data; hosting owner TBD |
| PostgreSQL Flexible Server / pgvector | Advisor relational state, snapshots and curated retrieval | Advisor-owned database/instance; approved hosting tier TBD |
| Cosmos | Tracking container/database | App entities on approved capacity |
| Service Bus | Topics/subscriptions/queue | App entities on shared namespace |
| Blob | Private photos | Application |
| Foundry | Inference | Project/platform allocation TBD |
| ACR | Images | Shared registry with scoped access |
| App Configuration/Key Vault | Config/secrets | Shared services, scoped application access |
| App Insights/Log Analytics | Telemetry | Approved isolation/workspace |

## Environments

Local uses synthetic data and compatible emulators/controlled cloud resources. Development consumes shared platform with isolated entities. Test is reproducible with synthetic data. Production has separate identities/data and protected deployment. Development sharing does not automatically justify production sharing.

## Required platform inventory

Capture IDs, regions, tiers/capacity, network rules, deployment/data-plane roles, backup settings, owner/support and cost allocation. `existing` declarations neither grant permission nor prove isolation. Shared SKUs are changed only by their authorised owner.

Cost scenarios include fixed hosting, data capacity, messaging, storage, PostgreSQL/vector workloads, edge, telemetry and AI usage. Budget alerts need response actions and do not alone stop spend. Budget is not set; estimate costs, document tier tradeoffs and obtain applicable spending/deployment approval. Exposure, retention and recovery still need acceptance.
