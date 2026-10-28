# v156 — Authenticated 2022 Global dungeon-finale reward chain and save-migration gate

## What the original 2022 archive actually establishes

The owner's original `mst-decoded.zip`, SHA256 `69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9`, contains 2022 `F_MISSION_MST_1_Ver1118.json` (SHA256 `d4e364b6c1c5a825c0153c57bdd4123cd35800c74db795d913d119b6c9a99f83`). For **all 29** archived `missionRewards='8:0:1:0:0'` missions in the previous v155 source ledger:

1. The reward-bearing quest is the **last quest of a unique original dungeon** — 29 separate dungeons, not 29 arbitrary encounters.
2. Its original `requiredMissionIds` exactly matches the **immediately preceding quest in that dungeon** (29 of 29 chains).
3. The dungeon contains **3–6 story missions**, each with its own original ID. The existing v142 live-quest source join confirms **22 first-region finales currently playable**. The v147 original Amdahl source confirms **seven finales** (404,414,424,434,444,454,465) that remain **unplayable**.
4. These are the specific source destinations for a potential first-clear award. Historical descriptions and matching original achievement reward enums strongly support one Gem per final clear, but exact 2022 server payout/claim and retroactive owner migration remain unverified.

The new canonical v156 tuple `[missionId,dungeonId,requiredPreviousMissionId,missionCountInDungeon,liveIn106Quests]` is SHA256 `0086bcd4f08b1fc6a748c800f5444221afbb1c1a6fc749e9c7e593111498b3c8`. Its original v155 source reward inputs are SHA256 `de8bde1cbee451e3c1b07c8b3e47afd38bc0465787b2b4aa6f5c8a620c4c83a7`. All original-source rows are independently recomputed from the owner's source ZIP when `BF_ORIGINAL_2022_MST_ZIP` is provided.

## Critical current save implementation finding

The **actual current APK-bound HTML** still defines `defaultProgress()` with `version:7`, `questClears:{ }` and **no Gem balance field**. `parseProgress(data)` explicitly reconstructs allowlisted fields and does not restore any Gem balance or one-time Gem claim ledger. `awardDemoRewards()` increments `P.questClears[QUEST.missionId]` on **every replay**; it does not distinguish first clears from replays before writing. Simply incrementing a hypothetical `P.gems` would **lose that value on reload**, while rewarding without a durable claim ledger risks repeating the payment. Both are unacceptable.

For a future **actual gameplay** patch, first design and verify a separately tested save-safe migration, one-time first-clear ledger and rollback/restore/recovery semantics, explicitly deciding how old v124 saves with already-cleared quests are handled. Test corrupted v7 saves, old saves with no quest clears, repeated clears, crashes between payout and save, overflow, export/import, and no Amdahl rewards. Original Gem earning and consumption need clear attribution to the authentic gameplay layer, separate from DEMO catalysts and summons.

## Actual v156 scope

**Source data + regression only**. Adds an exact 29-dungeon provenance/chain fixture and an automated fail-closed check against already verified v142, v147 and v155 source manifests. The test pins the current save format and absence of a live Gem wallet so no developer can mistake v155's source-only panel for a working payout.

No Java/Android files, APK gameplay or UI, rewards, saved data, balance, quest unlocks, title graphics, signing or network permissions change. Existing **106 playable quests, 72 playable forms and v7 saves remain untouched.**

Verify exact feature-head GitHub CI, guarded merge and subsequent merged-main CI. Issues #80 (Gem first-clear economy), #78 (Merit and 7★ evolution), #75 (2022 enemy AI/waves) remain separate outstanding work.
