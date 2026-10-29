# v189 — Opt-in, source-perfect historical BF1 battle illustration gallery

**Status: independent Claude review required before merging; Android-facing feature branch only.**
Baseline: owner-tested v188 merged-main Build #829, `604d07753409da00adb0fd2ed98850dd4a050c2f`.

## What users can see

In **Units → Original Global Unit Archive**, a SECOND, separately **default-off**
checkbox offers **67 historical BF1 battle illustrations** in each relevant
unit's Details panel. The image is the original archived **108×108**
`unit_ills_battle_ID.png`, presented with a source-era warning:
"Historical BF1 battle illustration · exact 2022 Global battlefield assignment unverified".
Images are **not** displayed in live fights, enemy encounters, summons, quest
screens or automatic 2022 opponent selection.

This complements rather than modifies the v188 optional **54 unit thumbnails**
and preserves the original **127 curated 2022 archive thumbnails**. There are
**54 historical IDs** whose regular 2022 curated thumbnail is absent, plus
**13 earlier historical IDs** that already had a curated thumbnail; the 67
battle illustrations are a separate visual asset class.

## Provenance and build

The build reads **only pre-existing, SHA-pinned v184/v185 repository sources**:

- v184: original-byte bundle SHA256
  `1c450f3487cbb4ec4c6a7103d35ec5b6680d575de4094c6fc39f0ff4084d9914`;
  three nested 18-unit provenance parts and **54** battle illustrations.
- v185: original-byte 13-unit bundle SHA256
  `81136fa4ba29f7d8a58da3d5583ea10536c6d2ba48d383338d94dfa6b9e5dd3a`;
  source ledger for the **remaining 13** battle illustrations.
- v183: archived 54 unit thumbnails' ledger SHA256
  `0030b4bac35055b4ca5c4791464f56e406a37e74d4c9539f46711da8289734fd`
  used to cross-check the disjoint 54+13 ID sets.

Every staged PNG must match its *original ledger* by byte count and SHA256,
have a PNG signature, and be exactly 108×108. All 67 ship to **a new
isolated folder** `assets/content/unit_historical_battle_archive/`, without
overwriting `unit_archive/`, `unit_historical_archive/`, or source ZIPs.
The compiled-APK test independently reads the original nested source ZIPs
and compares every APK image to its source entry *byte for byte*, with exactly
67 paths and no extras.

## Runtime and safety

The new archive checkbox is independent of v188; neither state is saved.
Preview image errors show **ART PENDING**. No animation is inferred from
source PNG/CGG/CGS. No new gameplay resource, save migration, combat actor,
AI, summon, enemy placement, equipment, item, Gem, Imp, reward, event, network
permission, Android identity, signing rule or owner v7 save format is changed.

**Historical BF1 bytes are NOT evidence of exact 2022 Global battle sprite
assignments.** No claim of native 2022 waves, enemy levels, formations, AI,
drops, original renderer or native animation timing is made. Research bank
source-only v184–v187 semantics remain unchanged.

## Verification and mandatory release gates

- `prepare_bf_historical_battle_illustrations_v18900.py`: strict source
  ZIP + provenance+SHA/Png/IHDR validation and collision-safe staging.
- `test_bf_historical_battle_gallery_v18900.py`: Chromium checked-default,
  both independent checkboxes, 54+13 representative images at 108px, unloaded
  source fallback, idempotency and no changes to player `P`, combat `S`,
  `bf_global_offline_demo_v7` or storage write count.
- `test_bf_packaged_historical_battle_gallery_v18900.py`: actual compiled
  APK exact source bytes, 67 paths, source disclaimer, separate unchecked
  checkbox, existing 127 curated +54 v188 PNG count, unchanged v7 marker.
- Existing entire v188 test suite still runs unmodified. Build and smoke test
  on an Android device required before claiming owner-release validation.

**Do not merge until** the feature's exact-head GitHub Actions build is
successful and independent Claude review returns **APPROVE** with all blockers
resolved. On review changes, require new exact-head CI. After merging, require
fresh merged-main CI and owner-device smoke test before recommending replacing
the currently confirmed working v188 APK.
