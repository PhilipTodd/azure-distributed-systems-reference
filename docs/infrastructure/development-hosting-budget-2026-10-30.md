# Development hosting budget revision — 30 October 2026

Status: Revised whole-portfolio budget accepted by the owner; provisioning/verification pending.

## Current direction

The owner confirmed that Parameter Pilot, BlastIQ and Ticketing are education/demonstration projects with only the owner developing/testing them, and requested total hosting below $80 if possible, retaining the existing B1 plan. Interpret this as an **A$80/month total hosting planning target across all three products**, using the billing currency and preceding AUD discussion; this is an explicit working assumption, not a new additional A$80 allowance. It is not a production availability/SLA target or an automatic billing cap.

- Retain `asp-platform-dev` at B1 with one worker. Withdraw the proposed B2 upgrade; no scale operation is requested.
- Include one classic APIM Developer unit for educational purposes, per the owner's subsequent explicit direction. Its estimated A$68.40/month is included in the total below. This supersedes its earlier withdrawal; no deployment has occurred.
- Preserve accepted service ownership, identity, authorisation and secret isolation. Low traffic does not authorise weaker access controls or silent changes to ADR-026.
- Keep PostgreSQL/Advisor, photos, unused broker entities/workers and Test/Production deferred to their authorised stages. Do not delete existing shared resources or affect other products merely to reduce cost.
- Keep configuration stores Free initially. ADR-031 now accepts PP ownership of exclusive service-isolated stores/vaults, with provisioning deferred to PP Bicep changes. This ownership correction does not add a paid tier or new budget.
- Assess any new fixed charge against the whole portfolio target. No A$120 incremental allowance from the earlier proposal applies.

The owner subsequently accepted the revised A$118.41/month estimate (approximately A$120/month) before tax and additional variable usage, stating that steps may be taken later to reduce costs. This replaces the former A$80 target as the current planning baseline; see the [acceptance record](../engineering/authorised-decisions-2026-10-30.md). It is a total portfolio budget estimate, not an incremental allowance or hard billing cap. Budget approval does not initiate deployment or accept unrelated architecture/retention proposals.

## Recalculated monthly estimate including APIM Developer

Use a 730-hour month (30.4167 days). A dated Cost Management daily query returned 28 rows for 1–28 October UTC, totalling A$39.38693 pre-tax; exclude 29 October's partial A$0.58811 row. Normalise those 28 days to 730 hours: `39.38692995835624 / 28 * (730 / 24) = 42.786397...`. No B1 charge is added again because it is already included in the current-subscription baseline.

| Component | Monthly AUD estimate, before tax |
| --- | --- |
| Existing whole-subscription hosting run rate, including B1 | A$42.79 |
| One APIM Developer unit, A$0.0937/hour x 730 | A$68.40 |
| Planned ACR Basic, A$0.2373/day x 730/24 | A$7.22 |
| Two proposed Free App Configuration stores | A$0 |
| Proposed Standard Key Vaults | Usage-dependent operations; no fixed charge included |
| **Estimated total with planned ACR** | **A$118.41/month plus new variable usage** |

With APIM but before adding ACR, the estimate is A$111.19/month. Adding the planned ACR brings it approximately A$38.41 over the A$80 target. The current baseline includes all subscription resources, potentially unrelated resources, not just the three products. It is a run-rate calculation, not Azure's forecast API or a final invoice. Existing reported telemetry/storage/network spend is included; any incremental telemetry, storage, certificates, Key Vault operations and egress are not predicted. Public meter rates may differ from the account's offer; tax/credits and reporting lag remain excluded. Requote before deployment. PostgreSQL remains deferred, and there is no B2 delta.

## Actual cost evidence

A read-only Azure Cost Management ActualCost/MonthToDate query grouped by ServiceName on 30 October returned A$39.98 pre-tax across the current subscription. Rounded components were App Service A$19.28, SQL Database A$14.97, Log Analytics A$4.90, Storage A$0.80, Bandwidth A$0.01, with Cosmos and Service Bus reported approximately zero in that query. Components are independently rounded; do not treat them as invoice reconciliation.

This covers the subscription rather than only these three projects, may include unrelated resources, is incomplete for the month, and may reflect delayed reporting. It is neither a forecast nor a guarantee of the next bill or free Service Bus. No credits/tax/subscription-discount assumptions are inferred. Reconcile closed-month actuals and the resource breakdown before committing more spend; monitoring existing ingestion/storage is more useful than assuming all services are free at low traffic.

The public [retail-price evidence](platform-pricing-2026-10-30.json) remains an estimate of individual meters. B1 retail baseline is approximately A$19.78 per 730-hour month. ACR Basic would add approximately A$7.22/month; two Free configuration stores have no instance charge; Standard Key Vault operations are usage-dependent. These are not a new total bill estimate. The former A$94.31 fixed-increase scenario is withdrawn.

## B1 capacity and low-traffic operation

Owner-only traffic makes shared B1 a reasonable development constraint to try, subject to measured operation. The [inventory](platform-readiness-2026-10-30.md) still shows approximately 79% average memory and 93% peak for four existing apps; idle app/Functions memory and background activity do not disappear with minimal visits.

Keep API startup/concurrency/telemetry proportionate, add only currently required applications and verify their actual footprint. Do not automatically scale the plan or disable another project's app/Always On/background work. If B1 cannot run the authorised slice safely, present measured results and options such as owner-controlled demonstration schedules or Local execution; any changed required behaviour or Stage 1 exit criterion needs explicit review. Retaining B1 is not a claim that two more APIs have already fitted or passed performance checks.

## Superseded low-cost gateway investigation

The following Consumption alternative was identified before the owner required APIM Developer. It is retained as background only, not the selected next step. APIM Developer preserves ADR-026's dedicated-address approach, subject to actual addressing and denial tests. No alternative ingress mechanism is required merely to satisfy the superseded cost-saving recommendation.

Investigate APIM Consumption rather than a fixed-cost Developer instance. Microsoft's [pricing page](https://azure.microsoft.com/en-gb/pricing/details/api-management/) lists an included 0–1 million operations band per subscription; confirm the applicable offer and operation definition before deployment. This could suit owner-only traffic, but is not yet a deployable approved design.

ADR-026 currently requires narrow source-address restrictions at public backends. [Consumption has no deterministic dedicated source address](https://learn.microsoft.com/en-us/azure/api-management/api-management-howto-ip-addresses), so it cannot silently replace Developer under that mechanism. Do not allow an entire Azure region or expose an otherwise unprotected direct backend to save money.

A candidate for a focused design review is Consumption plus cryptographic caller authentication for backend ingress, retaining customer bearer-token/owner checks independently. Published support for [APIM backend certificate authentication](https://learn.microsoft.com/en-us/azure/api-management/authentication-certificate-policy) and [App Service client certificates](https://learn.microsoft.com/en-us/azure/app-service/app-service-web-configure-tls-mutual-auth) makes certificate-based ingress worth assessing. Required work includes trusted-certificate validation (not just presence), direct-call rejection, distinct gateway versus Tracking-to-Aquarium callers, preserved OBO semantics, probes/deployment paths, certificate storage/rotation and compatible Local behaviour. This is an option for investigation, not an accepted replacement architecture, demonstrated security property or permission to install certificates.

If no suitable low-cost gateway design meets the requirements, present a deliberate Development topology/sequencing change for approval. Do not imply Stage 1 is complete or use a temporary unrestricted route as accepted infrastructure.

## Next preparation and controls

1. Carry forward one shared APIM Developer unit with B1 retained. Verify actual dedicated addressing and narrow backend restrictions under ADR-026; keep the model unchanged until applicable approved details are ready.
2. Rework the current platform resource schedule around B1 plus required APIM Developer and only necessary dependencies. Keep the approximately A$118.41/month total, ACR/store/vault grants and variable costs explicit; no deployment implied.
3. Reconcile actual closed-month/resource costs and set owner-approved portfolio cost alerts if later requested. Azure budgets alert; they do not cap spend. Do not create recurring monitors, alerts or automated resource shutdown from this document.
4. Provision only after the relevant architecture/platform/spend approval and a concrete validated template/what-if. Remaining SQL identity/isolation, Cosmos access, retention and operational verification gaps still apply.

The earlier [platform proposal](platform-change-proposal-2026-10-30.md) is historical input, superseded for B2 and its incremental allowance; its APIM Developer selection is now reinstated by the owner. Other unaccepted proposals remain unaccepted. No Azure setting, resource, platform code, access grant or retention value was changed by this revision.
