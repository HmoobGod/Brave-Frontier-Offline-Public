# v336 — Canonical v7 squad preset save receipt (source-only change)

Parent: `main` at `493f40feb216f6898835d24dd9e6b97d2e454c64` (merged #332). Independent of draft #335's manual Focus and Auto Repeat files.

## Gameplay defect and fix
The optional saved-squad preset feature called the native `saveProgress()`, but previously treated a truthy result as proof that the new squad was actually written to the canonical v7 player save. A stale, intercepted, or malfunctioning adapter could return true without committing the changed team, and the module would then reset the active battle as if the preset had safely persisted.

After a successful response, `applyPreset` now reads `bf_global_offline_demo_v7` synchronously, rejects missing, oversized, malformed, or wrong-version records, and requires that the saved squad be an array exactly equal (same IDs and ordering) to the requested owned preset. If any receipt check fails, it reverts the in-memory squad, exposes a recovery/export message, and **does not call reset or renderProgress**.

The guard is deliberately conservative: a storage implementation that cannot provide a verifiable canonical record cannot authorize a reset. There is no new save schema, no extra unit slots, no implicit restore, and no writes to the owner's installed APK or active save.

## Test gates
- `test_bf_qol_squad_presets_v10000.py`: Chromium gameplay regression covers an adapter returning true without writing, and an adapter writing the wrong squad while reporting true. Asserts the in-memory squad, existing canonical record (for no-write case), and reset count remain safe.
- `test_bf_packaged_qol_squad_presets_v10000.py`: packed Android asset contains the exact canonical receipt gate alongside existing app identity and v7 save checks.
- Existing successful, thrown, false-return, Auto Battle gap, busy, ownership, and deletion cases must all still pass.

**Promotion:** Fresh exact-head Android/Chromium/packaged/v7 save regression CI and independent source review. Remains draft until these conditions are met. No assertion of full 2022 combat/AI/formation/drop authenticity or new release APK.
