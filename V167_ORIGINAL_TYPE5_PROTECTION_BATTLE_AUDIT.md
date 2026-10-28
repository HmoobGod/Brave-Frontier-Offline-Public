# v167 — Verify and expose actual original-source elemental protection hit results

## Baseline
Fully verified v166 `main` commit `92897da8db452b3668655d1bc2b46fe2d22c4ba4`, merged-main GitHub Actions Build #584 run `40705805732` **SUCCESS** (197 steps). v166 activated source-authenticated 10% type-5 elemental leader protection for twelve playable archived forms in the existing archive DEMO combat path when the enemy's element is known.

## This revision
Add **battle-only, observer-only telemetry** to the existing type-5 protection hook, not a second damage modifier:
- Count each source-qualified matching-element incoming hit processed by that hook, including 1-HP hits where integer rounding produces zero prevented HP.
- Record the exact input and returned integer damage; sum their actual difference, rather than claiming 10% prevented at every rounding boundary.
- Keep at most 16 immutable in-memory entries; expose only the last eight through `BFGlobalOriginalElementResistV16600.snapshot().recent`. Include authenticated leader skill ID, known incoming element, DEMO wave/round, input, result and actual prevented damage.
- Reset per-battle telemetry when the game creates a new `S` battle object; never put counters into `P`, localStorage, backups or saved roster.
- Display the hit count and observed damage prevented inside the existing type-5 protection details panel, which remains explicitly labeled as **DEMO** baseline and source-qualified original 10% effect.

## Test gates
`test_bf_original_type5_battle_audit_v16700.js` performs source-join assertions for all twelve types against the original 2022 Global leader passive and English descriptions, exercises matching and unknown elemental attacks, exact hit reduction, damage saved, panel display, bounded event history, KO, training, inactive/unknown leader, encounter reset and repeat source-script loading. The existing v166 Playwright regression remains registered. `test_bf_packaged_type5_battle_audit_v16700.py` verifies the actual generated signed Android APK includes the correct battle hook, module, bounded ledger and canonical save code.

No modification to the incoming damage expression in `index.html`, no new original enemy-wave assertions, no automatic Gem/BC/HC payout, no damage or skill multiplier change, no Android signing changes. Native 2022 formula, precise rounding, stacking, unknown 2022 enemy elements and type31 Spark are still unverified.

**Required:** exact-head v167 feature GitHub Actions success, v166 verified main success, SHA-guarded merge, and green fresh v167 merged-main Actions before promoting to stable. Owner's installed v124 APK and actual device save untouched.
