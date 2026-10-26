# Brave Frontier Global v88.00 — Live Original-Source Normal Crystal Production

**Parent:** v87.00 successful Build #324, SHA 1290f3d7af51d048d04b39802b6e35e13707698e, signed APK artifact 12590624624. v88 is a candidate until its exact commit passes CI with uploaded signed APK.

## Real battle connection, original BC/HC production math
The original 2022 Global F_UNIT_MST_1/2_Ver1084.json provides 2,258 source-valid collectible normal-attack profiles with authenticated hit counts and separate dropCheckCount per hit. The v81/v82/v84 reference cores calculate base Battle Crystals (BC) at 35% per drop check and Heart Crystals (HC) at 10% per hit, using the documented integer RNG of 0..100 inclusive.

v88 hooks the real existing DEMO player performUnit normal-attack action. It samples original source drop checks only when an eligible living owned ally actually resolves a queued normal attack that damages an observable living enemy, and the exact v84 source unit profile is validated. A battle-side panel shows generated BC/HC counts. Session-only counters reset with the battle; guard, unknown-unit, missed and paralyzed actions cannot produce source events.

This is a genuine **combat-event integration**, not only a read-only catalog. **It is not native crystal pickup.** The produced counts remain uncollected reference rolls until recipient rules can be verified. It does NOT change BB gauge, heal HP, grant drops/rewards, spawn items, set enemy resistance, infer per-hit overkill, or alter the underlying DEMO damage. Base (non-overkill) rolls are explicitly used, rather than falsely inferring an overkill multiplier from total target HP.

## Provenance
- mst-decoded.zip original 2022 archive SHA-256: 69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9.
- Verified source tuple hashes and exclusions: source_data/bf_global_2022_full_normal_crystal_checks_v8400.json and research/RELEASE_V8400.md.
- DecompFrontier client remains incomplete; MissionStart server handler unsupported. No external server/library or incompatible source copied; 2014 formations not used as 2022 native truth.

## Gates
Retain P.version === 7 and bf_global_offline_demo_v7; package ID org.bravefrontier.offline; debug signature and INTERNET-free manifest. Complete new deterministic actual-normal-attack, guard, invalid-source and save-isolation Playwright tests; retain inherited browser suite and Android signing/package regression, with uploaded artifact. Android phone testing remains separate.

Next: original recipient/pickup distribution, BC-to-BB conversion, HC healing and native hit/overkill timing evidence before enabling crystal effects.
