# Development API hosting and ingress

Version: 0.1 | Date: 20 October 2026 | Status: Accepted architecture; feasibility/configuration pending

## Compute

Separate containerised Aquarium, Tracking and later Advisor API apps on existing shared Linux App Service Plan; three service-owned worker Function Apps share that plan. Each has separate identity/deployment/configuration. Verify compatibility and headroom; source B1 defaults do not establish sufficient capacity. See ADR-011/012.

## Request paths

Browser -> shared APIM HTTPS -> selected API. API and worker -> required owner API over authorised workload calls. There is no browser bypass route to unprotected APIs.

Use App Service access restrictions on public backend HTTPS endpoints to allow verified APIM/workload source addresses and deny others. Independent access-token/resource checks stay in place. Publicly addressable does not mean unrestricted and does not mean private networking.

## Before implementing restrictions

- Inventory intended APIM tier and actual outbound address behaviour.
- Inventory API/worker effective egress addresses and sharing/change behaviour.
- Establish narrow reliable allow rules; no whole-region allowlist fallback.
- Specify verified deployment/SCM/probe access and operational management without opening browser backend paths.
- Prove approved calls work and arbitrary direct calls/forged credentials fail.
- If feasibility fails, return for a revised mechanism rather than weakening accepted access controls.

Front Door/WAF is deferred until release preparation; private networking is a later/revisited option. No actual addresses/rules or resources are configured by this document.

Authority: accepted [ADR-026](../architecture/decisions/adr-026.md), [ADR-011](../architecture/decisions/adr-011.md), [identity](../architecture/decisions/adr-009.md).
