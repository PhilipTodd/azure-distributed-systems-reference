# IaC and local topology

Version: 0.2 | Date: 19 October 2026 | Status: Proposed

## Bicep module plan

`web`, `api-hosting`, `identities`, `sql`, `cosmos-entities`, `messaging-entities`, `storage`, `configuration`, `observability`, `ai-integration`, `gateway`.

Subscription scope creates approved resource groups. Application modules operate at resource-group scopes. Shared-service changes are separate from application deployment. Environment files hold nonsecret parameters; Key Vault/identity handles credentials. Outputs never expose secrets or connection strings.

Existing Bicep establishes only resource group and Static Web App. Add approved modules incrementally with build/lint, parameter validation, exposure review and what-if. Do not claim module names above already exist.

## Local proposal

| Component | Endpoint/approach |
| --- | --- |
| Angular | 4200 |
| Aquarium API | 5101 |
| Tracking API | 5102 |
| Advisor API, later | 5103 |
| SQL development instance | 1433 |
| Azurite | Default emulator ports |
| OpenTelemetry collector | Configured OTLP endpoint |
| Cosmos/messaging | Compatible emulator where verified; otherwise isolated cloud dev resources |
| Identity/AI | Controlled development resources; deterministic test doubles |

Compose should use a named app network, persistent development volumes, health checks and nonproduction credentials outside source. Verify platform compatibility and feature coverage. Test cloud integration differences. Local ports are not public production endpoints. No runnable Compose definition is supplied by this Markdown pack.

## Accepted dependency changes — 19 October 2026

Add an Advisor PostgreSQL module (and local PostgreSQL with pgvector when Stage 5 is developed); remove planned Advisor Azure SQL/AI Search modules. Keep Aquarium SQL. Proposed local PostgreSQL port is 5432, subject to local conflicts. Engine/extension image/provider versions need verification.

API/gateway hosting must permit bounded photo multipart overhead while Tracking enforces the exact 5,242,880-byte file limit. No browser upload SAS configuration. Image workers retain originals and write WebP derivatives. Choose low-cost suitable tiers, prefer Australia East and provision later-stage resources only when authorised.
