# v191 — Seven original 2022 dungeon backdrops for 29 playable missions

**Status: feature branch, not released; independent Claude review required before merge.**

## Scope and source proof

The user's SHA-verified original 2022 Global master archive (`mst-decoded.zip`,
SHA256 `69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9`)
was already joined in v152 against the archived source original mission and
dungeon fields. The immutable v152 fixture is SHA-verified and has 142 2022
mission cross-reference tuples (106 playable, 36 research-only Amdahl).

Exactly **29 playable original 2022 mission IDs** match the **seven original
archived JPG background filenames** already retained in
`source_assets/bf1/dungeon/`:

| Original background | Exactly matching original playable missions |
|---|---|
| dungeon_battle_10200.jpg | 20,21,22,23 |
| dungeon_battle_10300.jpg | 30,31,32,33 |
| dungeon_battle_10400.jpg | 40,41,42,43 |
| dungeon_battle_10500.jpg | 50,51,52,53 |
| dungeon_battle_10600.jpg | 60,61,62,63 |
| dungeon_battle_10700.jpg | 70,71,72,73 |
| dungeon_battle_10800.jpg | 81,82,83,84,85 |

The user-owned 2022 source is the **background filename**, *not* original
enemy identities, positions, AI, damage, loot or battle transition timings.
In particular missions **70–73** use original background 10700 even though
their first opaque reference suffix differs. The patch uses the authentic
source background entry, not a naive first-token suffix guess.

All seven original archived JPEGs are individually guarded by **expected file
length and exact Git blob SHA-1**, and the original 10200 JPG is additionally
guarded by its earlier v27 original-source SHA256. The staging script cannot
overwrite an unlike asset; it copies the source bytes unchanged into the
APK's `content/dungeon/` folder. The compiled APK test independently
compares every one of the seven staged images with its source-original bytes.

## Gameplay visual change only, default OFF

The existing v38 **OPTIONAL ORIGINAL DUNGEON BACKDROP** toggle (default OFF)
now checks the strict original 2022 v191 source lookup first, then continues
to support the previous v38 event/cinematic fallback. It displays the
correct JPG only for a selected **unlocked** original supported Quest in
archive mode. No artwork is enabled in training battles or by default.

A new small **`bf19100_original_2022_dungeon_backdrops.js`** is generated
from the original 142-mission source fixture. Before exposing any of its 29
records it independently compares all records with the existing verified
v174 source cross-reference API, checks exact original images and live
mission IDs, requires 2022 provenance, and rejects any native enemy, wave,
AI or drop claims. Java loads this read-only gate *after* v174.

## Compatibility and tests

- No changes to `index.html`, 106-quest roster, enemy waves, player battle
  formula, drop calculations, quests or unlocks, P/S, original reward wallet,
  custom Gems, Imps, native animations, network permissions, package ID or
  Android signing.
- Existing canonical v7 save `bf_global_offline_demo_v7` remains intact.
- `test_bf_2022_dungeon_backdrops_v19100.py` checks all 29 source joins,
  seven JPG names, v38 toggle behavior, the mission 70–73 exception,
  training exclusion and no save/game state mutation in Chromium.
- `test_bf_packaged_2022_dungeon_backdrops_v19100.py` inspects the **actual
  Gradle APK**, compares seven full original JPEG file bytes, strict
  v38/v174/v191 load order and no save writes.
- Existing v38, v174, v188, v189 and v190 regression suites remain enabled.

## Gating

The last owner-tested Android baseline is **v188**, not this feature.
Do not merge before exact-head feature GitHub CI SUCCESS, prior v190 merged-main
Build #848 SUCCESS on exact commit
`f73a02a10303e4e275bd271c7801ac09e3450f2c`,
and independent Claude source/Chromium/API review. SHA-guarded merge must be
followed by fresh merged-main CI success. Upgrade to a newer APK needs
separate owner Android smoke tests for save compatibility, artwork and
the v190 Gem shortcut.

**No native original 2022 enemy formation or AI has been reconstructed by this patch.**
