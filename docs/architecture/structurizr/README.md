# Parameter Pilot - Structurizr Architecture

This directory contains the Structurizr DSL architecture model for the Parameter Pilot application.

The workspace loads the Microsoft Azure 2021 theme. Azure resource tags in `model/systems.dsl` and `model/deployment.azure.dsl` select its icons; `views/styles.dsl` styles the logical application elements. Structurizr Lite needs internet access to load the theme and icons.

## Decision update — 19 October 2026

Authoritative DSL now includes accepted Advisor PostgreSQL/pgvector consolidation, Tracking upload/5 MiB enforcement, Tracking-owned photo worker/WebP derivatives, and Advice history snapshot flow. Approval: [decision record](../../engineering/authorised-decisions-2026-10-19.md). Other candidate architecture remains unapproved where not separately accepted.

**Generated outputs are stale:** workspace.json and existing exported SVGs predate these source changes. Validate/render the DSL and regenerate exports before publishing; never treat stale generated output as current architecture. See [remaining reconciliation](../c4.md).

## Run locally

From the repository root, run Structurizr Lite with the directory mounted:

```powershell
docker run -it --rm -p 8080:8080 -v "C:\Git\azure-distributed-systems-reference\docs\architecture\structurizr:/usr/local/structurizr" structurizr/lite
```

Then browse to:

```text
http://localhost:8080/
```

## Views

- System Context
- Container
- Record aquarium parameter
- View parameter trends
- Generate maintenance advice
- Upload via Tracking and generate WebP images
- Browse historical advice and submitted parameters
- Azure deployment

## Important DSL structure

External software systems such as Microsoft Entra External ID and Stripe are declared at the model/workspace scope, rather than inside the Parameter Pilot software-system declaration. This is required by the Structurizr DSL grammar.
