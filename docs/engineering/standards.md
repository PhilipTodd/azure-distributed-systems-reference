# Engineering standards

Version: 0.4 | Date: 20 October 2026 | Status: Proposed

- Accepted ADR-028: .NET 10/ASP.NET Core 10, C# 14, EF Core 10 for relational data with compatible providers. Pin exact supported SDK/runtime/packages; verify Functions isolated .NET 10/extension hosting compatibility.
- Accepted ADR-028: Angular 22, strict TypeScript/templates, feature-oriented standalone components, client-side SPA and Vitest/Angular TestBed; no initial SSR. Verify/pin compatible supported Node/TypeScript/tooling and commit lockfile.
- Nullable C#, strict TypeScript, useful analyzers/EditorConfig/ESLint.
- Domain testable without Azure; explicit API/event mappings, no persistence entity exposure.
- Async I/O with cancellation; bounded timeouts, retries, concurrency and payloads.
- Retry only transient failures when operation semantics are safe.
- Optimistic concurrency and idempotent asynchronous handlers.
- Shared building blocks are technical primitives, never a shared domain model.
- Version contracts and migrations; document degraded behaviour and recovery.
- Review compatibility/licensing, including FluentAssertions, before dependency selection.
- Never weaken tests, security controls or analyzers to obtain a pass.

## Verification

Accepted ADR-030: use xUnit and separately approved assertion tooling; Vitest/Angular TestBed; meaningful integration, contract and authorisation tests; critical Playwright Test/TypeScript journeys. Run small Chromium PR suites and broader Firefox/WebKit checks before releases. Applicable builds/static analysis/tests must pass; failures block merge. Report skipped/unavailable checks. No blanket coverage percentage initially. AI adds versioned evaluation gates. See [testing strategy](testing-strategy.md), including synthetic data and protected browser artefacts.

Dependency rule and ownership: [services](../architecture/services.md). Task completion: [Definition of Done](definition-of-done.md). No build/test entry points are invented while application projects are absent.

## Accepted worker baseline — 20 October 2026

See [asynchronous-processing design](../architecture/asynchronous-processing.md). Service-owned workers use only their owner's stores; core CRUD stays synchronous with local outboxes. Advice/photo handlers are durable asynchronous workflows. One namespace routes relevant commands/events; direct telemetry is not a queued business task. Shared-plan compute requires capacity/concurrency verification.

## Accepted dependency and structure policy

ADR-002 accepts proportionate Clean Architecture: Domain/Application independent of Azure/HTTP/persistence, Infrastructure adapters, API/Functions hosts calling shared service-local use cases. Share only technical utilities between services. Avoid unnecessary interface/repository wrappers.

ADR-028 selects direct Cosmos .NET SDK inside Tracking Infrastructure, EF Core 10 for relational stores; exact provider/client/library versions/licensing remain to be verified. Use reviewed supported patch PRs and no previews by default. See [technology baseline](technology-baseline.md). ADR-029 accepts hybrid local dependencies with real-Azure verification for cloud-specific behaviour.
