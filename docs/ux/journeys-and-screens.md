# Personas, journeys and screens

Version: 0.4 | Date: 21 October 2026 | Status: Draft

| Persona | Need |
| --- | --- |
| Aquarium owner | Fast entry, reliable history, clear trends and maintenance |
| Premium owner | Contextual advice, transparent usage and billing |
| Operator | Failure diagnosis/recovery, privacy and cost control |
| Knowledge maintainer | Reviewed/versioned reference corpus; internal workflow initially |

Navigation: Dashboard, Measurements, Maintenance, Charts, Advice, Aquarium. Advice is the screen name; Advisor remains the service name. Account/subscription live under the user menu. Advisor is a later-release feature, not a nonfunctional first-release link.

| Screen | Behaviour |
| --- | --- |
| Dashboard | Tank selector, latest readings with age, upcoming tasks and activity |
| Measurements | Familiar panel, explicit units/measured time/test method/notes; preserve failed input |
| Maintenance | Planned/completed views; reschedule, cancel and complete |
| Charts | Time/parameter filters, units, missing-data gaps and optional overlays |
| Advice | New request, context/data warnings, asynchronous state/citations; scrollable prior-advice list and detail with original submitted parameter values |
| Aquarium | Profile, timezone, water volume and versioned definitions |
| Account | Entitlements, usage and approved export/deletion workflows |

Journey: sign in -> choose tank -> enter panel -> confirm saved -> inspect chart -> log or plan maintenance. Later: review context -> request advice -> see queued/running/terminal state -> inspect cited result.

## Interaction rules

- Never substitute zero for missing data.
- Distinguish measured, effective and recorded timestamps.
- Keep failed form input available for session retry.
- Label correlation rather than asserting causation.
- Separate owner observations from AI interpretation.
- Advice states: queued, running, completed, failed, cancelled.
- Keyboard support, labelled fields, accessible errors and non-colour chart cues.
- Target WCAG 2.2 AA with automated and manual keyboard/screen-reader checks.
- Entitlement gating explains access; historical owner data stays accessible under approved policy.

Wireframes, responsive breakpoints and chart library selection remain design-readiness work. No finished UI is claimed.

## Accepted Advice and photo interactions

Advice is a request/result history, not continuous chat. Cursor-based scroll-back exposes older advice; selecting a result shows its original submitted parameter values, units and measured times. Do not substitute current readings. Recheck access on history list/detail. No photo attachment or image context is offered for advice in this pack.

Photo selection checks exact bytes and shows “Maximum photo size is 5 MiB (5,242,880 bytes)” before upload. Handle Tracking's 413 similarly. Upload through Tracking, then show processing status. Future gallery uses cropped 400 x 400 WebP thumbnails; selecting one opens the padded 1200 x 800 WebP hero. Keep the original for future processing; it is not the default gallery display.

## Accepted measurement entry and retry

Fetch selected definitions/units/current revisions from Aquarium for the selected tank. Submit a panel to Tracking. A stale-definition rejection offers configuration refresh and revalidation without discarding user input; an Aquarium dependency failure keeps entry data available for retry and never displays saved success. Historical reading display queries Tracking. See [ADR-023](../architecture/decisions/adr-023.md).

## Accepted profile preference and minimum tank contract — 21 October 2026

PROFILE-01/TANK-01: after first External ID sign-in, require an unselected measurement-system choice: Metric, US customary or UK imperial. Complete profile before tank creation/measurement entry. Users may later change this preference. Tank creation follows the [minimum contract](../api/tank-and-profile-contract.md), showing explicit litre/US-gallon/UK-gallon volume units and a user-confirmable timezone suggestion. Do not silently default measurement preference. Historical advice remains as originally issued.
