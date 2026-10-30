# v206 — Original 2022 Amdahl Story & Quest Guide (read-only UI)

**No playable 400-series quests, no original enemy rosters recovered, no
quest unlock, no save schema changes, no Gem/Imp economy changes.**

The existing v149 Amdahl map already shows the original area and seven
original battle backgrounds, and v151 already lists the 36 opaque encounter
references. Neither gives players the complete **original 2022 English
quest descriptions and source reward/energy schedule** in that map view.

v206 adds a read-only in-game guide directly underneath the existing Amdahl
map preview. It shows each of the 36 original source mission names,
descriptions, prerequisite IDs, source wave **counts** (not formations),
Energy costs (not charged), EXP, Zel and Karma. A dungeon dropdown and
existing map pins navigate all seven original dungeons, including the
six-mission final Amdahl Castle.

## Sources and hard bounds

Original source: `source_data/bf_global_2022_amdahl_quest_readiness_v147.json`,
whose authenticated owner master and English localization provenance is
pinned in the existing v147/v149/v151 source checks.

- Original 2022 mission master SHA-256:
  `d4e364b6c1c5a825c0153c57bdd4123cd35800c74db795d913d119b6c9a99f83`.
- Original v147 quest canonical SHA-256:
  `f35a7b06bc9e6fae6facc1fd77422f74c04798da4fb87f64a2737a0483a572c3`.
- Source mission IDs: 400–404, 410–414, 420–424, 430–434, 440–444,
  450–454 and 460–465 (36); seven original dungeon maps.
- Amdahl starts after St. Lamia mission 365. This prerequisite is
  displayed as evidence, **not applied as a new playable unlock**.
- Source wave counts are used only for display; no native ordered
  formations, battle entities, drops, AI or mimic chance are inferred.

## Implementation

`app/src/main/assets/bf20600_amdahl_source_quest_guide.js` contains
exact 36 source tuples; uses DOM `textContent` only, not original
untrusted HTML; checks v7, the existing 106 playable quests, the v149
non-playable original map and v151 source-only encounter ledger before
activating. It adds a details guide and dungeon selector underneath
`#bf14900-amdahl-art`. No new quest entries are inserted into `QUESTS`.

`MainActivity.java` loads the guide **after** v149/v151, as a
separate optional APK script, so failure does not interfere with
existing gameplay. No Android permissions, signing, Java bridge,
networking, save or battle engine changes.

`test_bf_amdahl_source_quest_guide_v20600.py` asserts all 36 rows
exactly equal the v147 source, tests seven dungeons and final six
entries, source metadata, malformed environment fail-closed, duplicate
injection, map-pin navigation, and no mutations to P, S, QUESTS or
a legacy `bf_global_offline_demo_v7` save. Node syntax and Chromium
tests are registered in the full Android CI.

## Merge gates

The exact-head APK CI must pass. Because this changes user-visible
Java/WebView integration (though not mechanics), request independent
Claude review before merging v206. Treat v206 as **read-only original
source presentation**, not gameplay completion. Device/saved-progress
validation remains outstanding.
