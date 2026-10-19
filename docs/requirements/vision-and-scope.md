# Product vision and scope

Version: 0.2 | Date: 19 October 2026 | Status: Draft; first-release direction confirmed

Parameter Pilot helps aquarium keepers record water conditions and maintenance, understand changes over time, and obtain contextual AI assistance grounded in their history and curated references. It replaces spreadsheet friction while demonstrating understandable, operable Azure distributed systems.

## Release scope

| Stage | Capability | Exit condition | Status |
| --- | --- | --- | --- |
| Foundation | Identity, tank setup, local/delivery/telemetry foundations | Secure end-to-end tank access | Proposed sequence |
| First public release | Tracking, maintenance and charts; observations and custom parameters support these journeys | Functional, isolation and recovery checks pass | Confirmed release direction; details proposed |
| AI/commercial release | Contextual advice, curated retrieval, entitlements and payment integration | Approved quality, quotas and billing reconciliation | Later scope confirmed; packaging proposed |
| Expansion | Photos and deterministic dosing | Reviewed upload lifecycle and formula catalogue | Scope retained; timing TBD |
| Accounting | Xero integration | Mapping and reconciliation approved | Scope retained; timing TBD |

## Assumptions

- Confirmed: general aquarium tracking, including freshwater and marine; not marine/reef-only.
- Confirmed: single-owner tanks and Australia East preference. Budget is unset; select appropriate resource tiers to keep hosting costs low.
- Domain supports multiple tanks; free/premium limits and pricing remain TBD.
- Free tracking and paid AI are intended.
- No autonomous dosing, physical control or separate administrator product. Photos are excluded from AI advice context throughout this pack.
- The illustrative 450-litre tank is not an owner fact or normative safe range.

## Success measures — proposed

- A returning user records a familiar panel within 60 seconds in usability testing.
- Users inspect historical trends alongside maintenance/dosing records without implied causation.
- At least 80% of approved AI evaluation cases pass the usefulness rubric; all release-blocking isolation/safety cases pass.
- Failed publications, jobs and integrations are detectable and recoverable.
- Every implementation story links to approved design and verification evidence.

Payment provider, Xero timing, photo/dosing release placement and detailed commercial policy remain open. No requested feature is silently removed.

## Authorised refinements — 19 October 2026

Photo uploads through Tracking are capped at 5,242,880 bytes; workers create cropped 400 x 400 WebP thumbnails and padded 1200 x 800 WebP heroes while retaining originals. Future gallery thumbnails open heroes. Advice uses a history list with request-time parameter snapshots, not continuous chat. Advisor uses PostgreSQL/pgvector for relational state and curated retrieval, replacing proposed Advisor SQL/AI Search. See [authorisation record](../engineering/authorised-decisions-2026-10-19.md).
