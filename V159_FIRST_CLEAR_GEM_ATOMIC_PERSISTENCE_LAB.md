# v159 — Executable, research-only single-key Gem persistence prototype

## Why this is a prerequisite, not a live payout

Owner-original 2022 Global mission masters and independent 2015 Global `clear_bonus:[{"gem":"1"}]` evidence (v155–v157) corroborate a first-clear Gem reward on exactly **22 currently playable dungeon finales**. Seven separate Amdahl finales are still source-only. v158 introduced 10,000 deterministic, pure-Python quest transaction simulations, but **did not prove an actual browser-persisted replay-safe transaction**.

The existing production game still uses `P.version===7` and the `bf_global_offline_demo_v7` localStorage key. Its saved progress parser does not implement or restore a native Gem wallet/claimed-finale ledger. **Do not insert an isolated live Gem wallet keyed separately from the quest-clear save**: those two writes would not be atomic as a pair, allowing crash-induced double grants or incorrect clear counts.

## New implementation in this checkpoint

- `research/bf15900_gem_atomic_persistence_prototype.js` is an executable, standalone **research harness**, not an APK asset and not referenced by Android's MainActivity or live game HTML.
- It verifies that candidate Gem wallet + replay ledger + quest-clear counter can be serialized in **one new research-only browser-storage key**. The existing owner v7 game save key is never accessed or modified.
- Source-anchored 22 exact live finale IDs from v156, excluding all seven Amdahl IDs. Legacy v7 cleared finale IDs are carried into a **hypothetical quarantine ledger**, not given retroactive payout. The legacy reimbursement/claim policy remains unresolved; this is only a test case.
- The prototype validates a strict model schema, all IDs and counts, finite wallet safety bound, sorted non-overlapping paid/legacy lists, and one Gem per paid finale; it clones before applying, then commits the entire research model in one storage replacement.
- Browser Playwright verifies first award, replay exclusion, stale-legacy exclusion, Amdahl exclusion, crash before commit + retry, quota-error no-change, corrupted input rejection, no unexpected writes, v7 state untouched, unchanged Android package/signing/offline manifest and source manifests v156/v157. CI runs the test; production APK cannot load it.
- Model bound `999999` is only a regression safety bound, **not** an established 2022 native currency cap. No Gem purchase, Gem wallet, item grant or gameplay economy has been implemented or enabled.

## Remaining indispensable gate before original-game first-clear payouts

This prototype solves only **atomicity within a single research storage key**. It does **NOT** solve the production problem of writing a separate Gem sidecar and the existing v7 quest-clear key atomically. Before any live Gem rewards, design a single canonical, safely migrated owner-save envelope preserving all v7 fields, recovery backups, imports/exports, old v124 devices, initial owner balances and edge cases. Derive and regression-test original first-clear/claim semantics; obtain an approved legacy already-cleared policy. Confirm compatibility in the signed APK and on actual device when requested. Only then replace the DEMO reward path for 22 original 2022 finale missions.

The required CI flow: exact v159 feature-head green, after **v158 merged-main Build #540 green**; guarded merge; new merged-main build green before calling v159 verified. The installed v124 APK is untouched.
