# v174 — Original 2022 encounter cross-table and battle backdrop evidence

## Why this patch exists

The original owner's 2022 Global mission archive is already proven to supply **106 live story quests plus 36 Amdahl source-only quests**, each with an original source wave *count*. Actual native 2022 enemy rosters, ordered wave composition, AI, drops, and reward transaction behavior are **not decoded**. In particular, numeric pairs in the archived `MISSION_8f4NYKxb` text must not be promoted into guessed enemy IDs.

v152 independently joined the exact opaque mission reference strings with two other **original 2022** master tables, Grand Mission Spot and Raid Point, and the 2022 Dungeon master background filename. This patch makes those audited references available to the in-game source inspector, with a strict save/gameplay isolation gate.

## Exact source-backed observations

- **142** original 2022 missions are documented: 106 currently playable, 36 Amdahl research-only.
- Of those 142, **92** mission strings exactly match at least one Grand Mission Spot record; **99** match at least one Raid Point record; **73** match both. These numbers do *not* establish actual enemy formation joins.
- **133/142** mission background filenames have the same suffix as the *first* opaque reference. Exactly **nine** do not: missions **70–73** and **230–234**. Neither matching nor differing suffixes decode any enemy.
- Original source wave counts are joined from the prior v142 live-quest and v147 Amdahl records. A source wave count does not supply ordered wave contents.

Provenance is pinned to the user's original 2022 `mst-decoded.zip` SHA256 `69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9`. The 142-row v152 canonical tuple SHA256 is `2acd1ab29b8a00b3c8804a89fdc9d7b99cba4853f5974f765bc7473c89e7a284`. The generator independently verifies hashes on both encoded and decompressed fixture bytes, source schemas, row order, and cross-table membership statistics.

## Implementation

- New deterministic build-time `prepare_bf_original_2022_encounter_crossrefs_v174.py` outputs `bf17400_original_2022_encounter_crossrefs.js` (small offline asset) from existing SHA-pinned original-source data.
- Java loads this JS **after** the existing v151 authenticated 142-mission source ledger. The module fails closed unless v151 provenance, v7, all 106 live mission IDs, all 142 exact raw strings, 36 Amdahl wave counts and cross-table summary counts reconcile.
- The existing quest inspector can display source background *filenames*, source wave counts and exact Grand/Raid **reference reuse** for the selected mission. Original source backdrops are **not substituted** into battles. The source-only Amdahl mission set stays unplayable.
- The module provides an immutable `window.BFGlobalEncounterCrossrefsV17400.lookup(missionId)` for future authenticated wave-engine investigation. It never grants enemy identities, AI behavior or drops.
- No localStorage calls, save/quest progression mutation, combat, EXP, energy, Gems, Imp bonuses, unit unlocks, Android package name, INTERNET permission, or signing configuration changes. The canonical save remains `P.version===7` and `bf_global_offline_demo_v7`.

## Regression and merge policy

- `test_bf_original_2022_encounter_crossrefs_v17400.py`: all 142 exact joins and 9 known nonmatches, representative UI selections including Amdahl, disabled native-AI claims, idempotence, fails-closed wrong save version, no save or game-state mutation.
- `test_bf_packaged_original_2022_encounter_crossrefs_v17400.py`: exact generated source bytes included in signed APK; Java load ordering, untouched v7 and no INTERNET, stable application ID/debug signing configuration.
- `node --check` verifies generated JavaScript syntax; all existing CI tests remain active.
- First verify prior merged-main v173 Build #701 SUCCESS. Require exact-head v174 feature CI SUCCESS, PR merge with expected SHA, then a fresh merged-main full APK CI SUCCESS before declaring v174 verified.

**No Claude review required** for this narrow immutable source-inspector module, which does not change gameplay, canonical saves, or claim validators. **Claude review required before** the next release that activates a native 2022 formation/AI resolver, alters battle reward distributions, or changes progression/save rules.

The owner's installed v124 and real save are not touched. This is not an Android-device test and not a claim of recovered 2022 native waves.
