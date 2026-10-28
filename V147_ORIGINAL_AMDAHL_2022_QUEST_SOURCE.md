# v147 — Original 2022 Global Amdahl (Palmyna) story campaign recovery

**Source-authenticated preparation for the next playable Grand Gaia region**, after St. Lamia. It does **not** unlock unverified enemy waves or change saves.

The owner's untouched 2022 Global `mst-decoded.zip` SHA256 `69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9` provides mission-master `F_MISSION_MST_1_Ver1118.json` (SHA256 `d4e364b6c1c5a825c0153c57bdd4123cd35800c74db795d913d119b6c9a99f83`) and dungeon-master `F_DUNGEON_MST_Ver1002.json` (SHA256 `16f090514d65846f6bd4a9998b50d6c810bc806a79858c0ff766cdb1a22536fc`). The owner's original `BF1_sgtext_part001.zip` SHA256 `4dccce4eeb6a89cc0cf5718badff7af95046c891882e42c05c6eaca81f9d6285` supplies English mission, mission-description, dungeon, and region names. Original source raw rows are retained in a deterministic compressed source slice; no invented translations.

Original 2022 Amdahl area/land **400/3** follows St. Lamia Mission **365**. Its **36 quests** are grouped into seven original dungeons:

| Dungeon | Original English name | Original backdrop |
|---:|---|---|
| 400 | Julep Village | `dungeon_battle_50100.jpg` |
| 410 | Ghost Ship Legnia | `dungeon_battle_50200.jpg` |
| 420 | Elios Plains | `dungeon_battle_50300.jpg` |
| 430 | Saji Mines | `dungeon_battle_50400.jpg` |
| 440 | Lamellia Temple | `dungeon_battle_50500.jpg` |
| 450 | Ghost Town Edila | `dungeon_battle_50600.jpg` |
| 460 | Amdahl Castle | `dungeon_battle_50700.jpg` |

The source manifest includes **every authentic mission ID, prerequisite, English title and description, dungeon, missionBattleCount (source wave count), Energy, EXP, Zel, Karma, raw mission-encounter reference string, raw reward field and source map/boss music filename**. Values are not approximated. Source exact digest of all 36 numeric/music/opaque-encounter tuples: `f35a7b06bc9e6fae6facc1fd77422f74c04798da4fb87f64a2737a0483a572c3`. Raw source slice canonical digest `758a2166fa728a3e11ce43c72ad11a18bba9dead78479c3ecef3d8354f041d1a`.

**What remains unverified:** 2022 native enemy wave IDs and formations, native enemy AI, drops, damage calculations, native mission scripting/quest-clear effects, world map coordinates/images, and source-authentic enemy sprites for this area. The original `MISSION_8f4NYKxb` is opaque; **do not interpret its tokens as enemy IDs**. No playable 400-series QUESTS were added, no P/S save mutation, no Android signing change. Existing 106 playable mission records and `bf_global_offline_demo_v7` are preserved.

**Next gameplay stage:** Recover and hash the seven original source battle background JPEGs and Amdahl world map/plate; add a safe next-region selector behind Mission 365 using original English source; adapt the 106-quest assumptions and test v7 saved progress; keep all unverified enemy wave/AI rewards explicitly DEMO until proven. Do not promote the raw data slice to live quests without those checks.

v147 is stacked on v146 feature commit (Death Magress art) and must wait until v141–v146 feature and merged-main CI gates succeed, then v147 exact feature-head CI and fresh merged-main SUCCESS. Owner remains installed at **v124** until a requested **v150** update.
