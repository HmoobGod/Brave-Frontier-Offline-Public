# Brave Frontier Global v63.00 — Exact Status Lifecycle Under Cure and Reinfliction

**Prerequisite:** exact CI-green v62.00 signed APK and v61's per-infliction `tokenFor(slot,code)` and selective `removeCode(slot,code)` status APIs. The 2022 translated item master continues to identify remedies #20200 (Poison, code 1), #20220 (Curse, code 5), and #20230 (Paralysis, code 6). The mechanics references remain independent community documents, not original executable recovery.

## Bug fixes

The existing v58 poison tick tracker, v59 Curse BB lock tracker, and v60 Paralysis action lock tracker keyed durations by live unit object alone. A status cured and then **reinflicted on that same living unit** could inherit an earlier `firstRound`, causing premature expiration or missing ticks. Each tracker now compares the unique status application token from v61. An application with a new token starts a new independent three-observed-turn lifetime; processing remains once per round.

These three effect processors also expire **only the matching status code** through `removeCode`, without executing a remedy item, so status-specific expiry cannot inadvertently clear coexisting ailments. The source-described full item cure behavior is preserved in v57's existing `cure(slot,itemId)` API. This patch deliberately introduces no automatic enemy skill infliction, additional damage, new inventory, speed changes, broader Auto Battle behavior or Sickness formula.

## Verification and preservation

New Chromium test covers Poison cure/reinflict/ticks and KO protection; Curse and Paralysis cure/reinflict/three-round expiry; source cure item still clears proper codes and concurrent ailments remain; unchanged `P`, localStorage and source data. All inherited Chromium suites, packaged Android verifier, original development debug signer, package ID `org.bravefrontier.offline`, absent INTERNET permission, v7 save marker and original art must pass. Native exact status timing, enemy proc data and wave-boundary effects remain unavailable. No promotion until exact GitHub Actions `success` with APK uploaded.
