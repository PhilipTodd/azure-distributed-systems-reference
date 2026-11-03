# Local dependency verifier

Non-feature .NET 10 console tooling for the [controlled Local setup](../../local/README.md). Database targets are constructed only from fixed loopback hostnames and checked Local port numbers; no Azure URL/token or developer credential fallback exists.

Uses the versioned synthetic fixture file and dedicated Local bootstrap database. The coordinator provides an ignored private runtime directory containing the Local SQL password, nonsecret port/path configuration and emulator public-certificate pin. Never pass a password as a command argument. Committed package lock and direct pins match the already used Stage 1 SQL/Cosmos clients; PKCS 10.0.14 overrides vulnerable transitive 9.0.4. No assertion-library licence is introduced.

The normal coordinator checks SQL Developer edition, repeatable seeds and rollback, Cosmos /tankId partitioning, repeatable seeds, wrong-partition 404, stale ETag 412 and same-partition batch commit/rollback. `--sql-only` allows independent verification of the approved SQL image while an emulator decision is pending. It never implies Cosmos passed.

This is not product ownership/feature testing or proof of emulator/Azure parity. Scientific seed definitions and actual Stage 2 migrations are not installed. Product SDK pinning remains Step 7.
