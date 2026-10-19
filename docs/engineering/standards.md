# Engineering standards

Version: 0.1 | Date: 8 October 2026 | Status: Proposed

- .NET 10/C# 14 are planning inputs. Pin compatible SDK/runtime/ORM/dependencies before implementation.
- Select supported Angular/TypeScript/test tooling; do not inherit historical version suggestions as permanent pins.
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

Use xUnit and approved assertion tooling; Angular component tests; meaningful integration/contract/authorisation tests; selected architecture checks and critical E2E journeys. AI adds versioned evaluation gates. Coverage measures inform review; percentages do not replace behavioural tests.

Dependency rule and ownership: [services](../architecture/services.md). Task completion: [Definition of Done](definition-of-done.md). No build/test entry points are invented while application projects are absent.
