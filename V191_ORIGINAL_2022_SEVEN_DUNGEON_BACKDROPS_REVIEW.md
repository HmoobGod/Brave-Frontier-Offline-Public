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

## C2 review follow-up — real chain restoration and regression

Claude's review of prior head `5d618307ecaec11938187aa488784e9c02624f6d`
found a significant coverage gap: v191's first browser test used a v174 mock,
while the native 2022 reference chain v108 → v109 → v151 → v174 was not
known to initialize in the actual prepared 2022 app.

**Independent root-cause inspection of the owner-tested v188 compiled APK**
found the embedded `BF_MORGAN_QUEST_DATA_V080` and
`BF_STLAMIA_QUEST_DATA_V090` globals had quests and dungeons but **no
`provenance` property**, whereas the already-existing fail-closed v108 and
v109 source gates require the original mission-master SHA. This is an old,
read-only reference integration bug; it does not imply the original quest
gameplay was missing. It explains why v174 and v191 could silently fail to
register in live Android WebView.

The feature now includes two tightly scoped **build-preparation-only** changes:
`prepare_morgan_quests_v080.py` and `prepare_st_lamia_original_v090.py`
preserve a minimal source-verified `provenance` object in the existing
embedded frozen record; they include only the previously asserted original
source ZIP/master SHA hashes and do not change the 36+36 source quest data,
story progression, battle state or player save.

**Local Chromium proof on the extracted original v188 APK HTML/scripts:**
once the two missing hash fields were inserted in memory, the actual v108,
v109, v151 and v174 scripts registered sequentially at 70 → 106 → 142 → 142
original source missions, with **no** JavaScript page errors. This local probe
used v188's actual packaged scripts; it is not a rebuilt v191 APK nor an
owner-device test.

Two additional hard CI gates prevent the same silent failure from recurring:
- `test_bf_real_original_2022_chain_v19100.py`: loads the actual *prepared
  106-quest game HTML* and injects the **real** original 2022 source scripts
  with no mocked v108/v109/v151/v174 global; checks that they all register,
  validate 29 new exact mission/JPG joins, keep 36 Amdahl research-only, and
  do not write the v7 save or alter P/S.
- `test_bf_packaged_real_original_2022_chain_v19100.py`: after Gradle
  builds the APK, requires that both Morgan/St. Lamia provenance records
  survive inside the **actual APK index.html**, and independently checks
  shipped v108/v109/v151/v174/v191 JS bytes and Java loader order.

**Review consequence:** The earlier Claude APPROVE WITH CONDITIONS applies
only to its old exact head. These preparation changes and new source-chain
tests require Claude to **re-review the delta on the latest PR head**. The
revised exact-head Build must pass before merging. Preserve the owner-tested
v188 APK while v191 release gates remain open.
