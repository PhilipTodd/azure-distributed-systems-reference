# Stage 1 B1 hosting and restricted APIM ingress

Date: 3 November 2026. Status: verified for the agreed Stage 1 feasibility scope; temporary resources cleaned up.

## Result

Run `cbac6e81bf93` passed eight initial network checks and all nine real customer hosting checks. Both private containers ran concurrently on the existing B1 plan. APIM accepted valid service tokens, rejected wrong audiences and tampered signatures, and direct backends rejected valid customer tokens from the owner's computer. Tracking used its actual managed identity/vault certificate for deployed OBO; Aquarium allowed the resulting read and rejected write, absent-token and wrong-audience requests from that permitted network origin.

The owner confirmed all nine checks passed and BlastIQ worked normally. Agent reachability checks returned 200 for the BlastIQ website; API root 404 responses establish reachability only, not functional correctness. The owner's functional confirmation is recorded separately from these probes.

The 15 available baseline one-minute memory averages ranged 76–83%. Nine hosting-window samples ranged 78–86%, with the latest at 86%; CPU ranged 22–94%, with the latest at 22%. Metric data lags and the window is short. This supports the minimal two-host demonstration on B1, not unmeasured product/worker capacity or performance. No scale change was made.

Cleanup passed: both PP hosts are disabled with public access disabled; original container/settings/logging and main/SCM restrictions restored; temporary APIs and grants removed; original registry conditions restored. B1 SKU, shared global policy and other application states matched their snapshots. Independent Azure readback confirmed both hosts disabled and only the pre-existing echo API remains. The Local verifier was stopped. Failed coordinator attempts remain recorded.

Evidence: [hosting and cleanup](evidence/hosting-ingress-verification-2026-11-03.json), [nine customer checks and owner confirmation](evidence/hosting-customer-verification-2026-11-03.json), [running health observation](evidence/hosting-health-observation-2026-11-03.json).

## Scope and authority

The owner instructed “Proceed” after the Step 5 work split described concurrent PP hosting, private container operation, narrow backend restrictions, APIM routing/token tests, evidence and shared-application checks. This authorises the bounded verification below. It does not authorise a plan upgrade, other-product configuration changes, new business features or Git publication.

Accepted [ADR-026](../architecture/decisions/adr-026.md) selects APIM Developer and restricted public HTTPS backends. [ADR-009](../architecture/decisions/adr-009.md) requires independent token, caller and operation-scope enforcement. The authoritative Structurizr workspace was consulted; this test does not change its topology.

## Verification mechanism

`tests/Stage1.HostingProbe` is a temporary, stateless .NET 10 container for the two existing PP App Services. It has health/read/scope-only write endpoints; it performs no SQL, Cosmos or business-data operations. Both containers run concurrently with a 128 MiB managed-heap limit per process; that limit is a test setting, not a measured total-process footprint or a selected product limit.

Tracking retrieves its existing versioned Development OBO certificate with its actual system-assigned identity, loads the key ephemerally and exchanges a genuine customer token for an Aquarium.Read token. Aquarium independently checks signature, issuer, audience, tenant, stable object ID, approved caller and scope. A read-only downstream write attempt must return 403. A same-network caller presenting no token or a Tracking-audience token to Aquarium must receive 401.

The coordinator adds two uniquely named PP verification APIs to existing APIM, using a unique path per run. Their complete inbound policies validate customer JWTs, UI caller and operation scopes. They deliberately do not inherit the shared bootstrap's unconditional 503 response. The shared global policy and existing APIs are preserved. CORS permits only the agreed Local and PP website origins; CORS is not an access-control substitute.

Only exact IPv4 /32 addresses are allowed: APIM's verified public addresses to both APIs, plus Tracking's complete `possibleOutboundIpAddresses` set to Aquarium. Main default action is Deny; SCM remains separately Deny with basic publishing disabled. App Service outbound addresses are shared with other applications, so the backend's independent token/caller/scope checks remain necessary.

Private ACR publication/pull access is temporarily restricted to the verification repository. Existing registry conditions are journalled and restored exactly; the temporary publisher assignment is removed. No registry admin credential is enabled or persisted.

## Execution and cleanup

Run `python scripts/run-hosting-verification.py --phase start`, then `--phase watch`. The start phase permits up to ten minutes for startup; individual network timeouts are retryable. The watcher allows fifteen minutes for owner browser verification and stops early if two consecutive available one-minute memory readings average at least 92%. These are temporary test safety thresholds, not product capacity acceptance targets. Azure metric reporting can lag.

The Local identity verifier detects the ignored `.hosting.json` file and forwards fresh customer tokens in memory to the isolated APIM routes. It records only check names/outcomes and run ID. No customer email, passcode, bearer token or private key belongs in evidence. The owner handles customer sign-in directly.

`--phase cleanup` is independently retryable. It disables PP hosts, restores original container/settings/logging and ingress restrictions, removes the two temporary APIs, restores registry conditions and removes temporary grants. It verifies that B1 SKU, the shared global policy and other App Service states are unchanged. The private immutable verification image is retained. No site-publishing password or SQL administrator password is used.

The initial run `c3f86d9609be` exposed coordinator startup handling: enabling an app did not start it, and a startup HTTP timeout ended the run. Run `1c9a1de97cea` stopped because Azure rejected a sub-minute PT1M metric query. Cleanup succeeded after both attempts and failures are retained in evidence. The coordinator now issues explicit start commands, retries startup network timeouts and queries at least two minutes of metric history. Three regression checks cover timeout handling, the minimum metrics window and hosting preparation without SQL/Cosmos operations. A successful retry must not erase these failed attempts.

During run `cbac6e81bf93`, a temporary exact owner-IP /32 SCM diagnostic exception was used to retrieve the successful container startup record with Entra authentication; basic publishing stayed disabled. It was removed immediately after diagnosis, before customer verification, while the main API rules remained unchanged. The Local verifier initially held port 4200 in a restricted process that Chrome could not reach. Only that identified PP process was stopped; a replacement listener was independently confirmed reachable and in hosting mode.

## Limits and remaining verification

Two minimal hosts fitting on B1 does not prove future product capacity, background-worker compatibility or a production availability target. Actual product images must repeat startup/health/resource and authorisation checks during their delivery. No Stage 2 ownership feature is implemented by this probe. GitHub authentication/publication/deployment execution and runtime/package baseline controls remain Step 7.

Address inventories must be re-read before each runtime deployment and after APIM networking/tier/recreation changes or App Service plan/address changes. Compare with the approved allowlist; update deliberately and rerun positive/negative tests. Never use a whole-region allowlist or silently keep stale rules.

Supporting Microsoft references: [APIM addresses](https://learn.microsoft.com/en-us/azure/api-management/api-management-howto-ip-addresses), [App Service outbound addresses](https://learn.microsoft.com/en-us/azure/app-service/overview-inbound-outbound-ips), [App Service access restrictions](https://learn.microsoft.com/en-us/azure/app-service/overview-access-restrictions).
