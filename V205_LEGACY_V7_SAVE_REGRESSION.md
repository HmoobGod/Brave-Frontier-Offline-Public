# v205 — Pre-Gem/Imp v7 save regression and fail-closed corruption gate

**Scope: test-only. No Android runtime source, quests, battle, rewards,
wallet, Imp balances or save schema changes.** The canonical Android
package and v7 save key remain unchanged.

## Why it matters

Older `bf-global-offline-demo_v7` backups predate the added personal Gem
wallet, original first-clear claim ledger and optional Imp records. A real
older owner v7 backup from the connected Brave Frontier/Save folder was
checked **privately** by loading a copy into the packaged game in Chromium.
Its saved roster, squad, unit EXP, quest clears, materials, EXP/Zel/Karma,
last selected mission and clear count all round-tripped without page errors,
quarantine warnings or rewriting the stored original JSON. **This is a
browser-level smoke of one backup**, not proof for the owner's current Android
v124 save, APK signing upgrade or every earlier save version. No real save
contents, checksum, player details or replay data are committed to GitHub.

## New reproducible synthetic verification

`test_bf_legacy_v7_save_loading_v20500.py` creates a private-data-free
legacy v7 JSON object from the game's own default roster, carrying only the
18 historical schema fields and intentionally **no** new wallet/Imp metadata.
It exercises the actual inlined browser load path with a fake in-memory
`localStorage`, checking:

- All roster, squad, unit XP, materials, currency, quest clears and mission
  selection survive initialization exactly.
- No free custom Gem balance or original Gem balance is created.
- All 106 packaged story quest-economy tuples retain the source-pinned
  v142 canonical SHA-256.
- The untouched original legacy save text is not automatically overwritten
  simply by rendering/initializing the game.
- A deliberately corrupted synthetic save referencing a nonexistent mission
  fails closed, is quarantined once, blocks autosave, and leaves the original
  corrupted data in storage for owner recovery.
- No JavaScript page errors are generated in either case.

The single new test is added to the existing Chromium-backed GitHub Actions
**full Android APK** suite, not the dependency-free source-only gate.
Local synthetic Chromium regression passed before publishing the test.

## Boundaries and next gates

The original source quest Energy/Karma visibility had already been
implemented by **v143**. No duplicate UI was introduced here.
The native original 2022 enemy-wave decoder and mimic encounter behavior
remain unrecovered; v205 does not claim them.

Complete exact-head PR Android CI before merge. Afterwards verify
the main-branch build separately and test an actual upgraded signed APK on
the owner's Android device and **current** save. Because this is a
test-only regression, independent Claude gameplay review is **not**
required for this PR; it will be required for future behavior/save changes.
