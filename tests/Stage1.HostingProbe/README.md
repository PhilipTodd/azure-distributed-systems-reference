# Stage 1 temporary hosting probe

Stateless verification tooling for the two existing PP Development hosts only. Pinned .NET 10 dependencies and a digest-pinned runtime image; no SQL/Cosmos or business-data access. Logging is disabled in the application. Tokens and ephemeral certificate material stay in memory.

Use the [controlled coordinator and cleanup runbook](../../docs/infrastructure/hosting-ingress-verification.md); do not manually expose this container or treat it as a product API. The test has separate gateway and backend JWT checks, approved caller and operation-scope checks, actual Tracking vault/certificate OBO and read-only downstream write denial. Health contains only service/run/start metadata. Every other endpoint requires a customer delegated token.

Verification paths and source-address rules are temporary and cleaned up after the bounded browser test. Product per-tank ownership and business operations are deliberately absent.
