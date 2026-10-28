# v155 — 2022 original Global dungeon first-clear reward source ledger

## Original 2022 Global evidence (archived source, not guessed drops)

The owner's original `mst-decoded.zip` SHA256 `69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9` contains:
- `3-mst-translated/F_MISSION_MST_1_Ver1118.json`, SHA256 `d4e364b6c1c5a825c0153c57bdd4123cd35800c74db795d913d119b6c9a99f83`. Exactly **29** of the 142 source-authenticated original standard story missions have `missionRewards='8:0:1:0:0'`. Exactly **22** are in the 106 currently playable DEMO quests, and **seven** are final missions 404,414,424,434,444,454,465 of not-yet-playable Amdahl. Canonical 29 three-column source tuples SHA256 `de8bde1cbee451e3c1b07c8b3e47afd38bc0465787b2b4aa6f5c8a620c4c83a7`.
- `F_GRAND_MISSION_REWARD_MST_Ver108.json`, SHA256 `f6e6a0c450c99045af81bcbdfffaab3e73845dd4e2240f04fd8d7fcfcc7705bf`. It independently contains 62 `rewardType=8` entries, including 45 with item ID `0` and amount `1` and original English descriptions e.g. **First Quest Clear Bonus**.
- `F_ACHIEVEMENT_SUBJECT_MST_1_Ver503.json`, SHA256 `36850eac317faf97f6196d8078b56d8a2594847eb2a727917b0d1bd1485efb56`. Four exact 2022 milestone rewards: ID 7000 `8:0:1:0:0`, ID 7020 `8:0:2:0:0`, ID 7040 `8:0:3:0:0`, ID 7060 `8:0:5:0:0`. Independent historical Global Achievement System documentation maps those specific milestones to **1/2/3/5 Gems**, corroborating the archival type-8 enum. See https://bravefrontierglobal.fandom.com/wiki/Achievement_System and https://bravefrontierglobal.fandom.com/wiki/In-Game_Credits (one Gem on stage completion).

The raw source strongly corroborates an original one-Gem stage first-clear reward; it does **not** independently verify the server's **claim delivery, retroactive migration, wallet/save schema, or stage completion transaction**.

## Implementation

A **read-only** collapsible source inspector under the existing original Quest encounter-reference ledger lists the original **29** fixed first-clear reward mission IDs, identifying the 22 existing playable DEMO missions and seven **non-playable** Amdahl finales. Selecting a source row displays the original raw payload `8:0:1:0:0`, one-Gem source interpretation and whether the current local DEMO save has any clear recorded. This is **not** a Gem transaction or claim status, and must not be presented as owner-installed or actually awarded.

The module fails closed if the authenticated 142-source / 106-playable v151 encounter ledger, live 106 quest list or v7 save state is missing or changed. UI is text-only, read-only, idempotent. All source rows pinned to original source and v142/v152 source manifests.

## Compatibility

No changes to original quest rewards, gameplay, enemy AI, currency, summons, loot, unit roster, Gems, save parser/schema, Android signing, package identity, backup/restore, network access or installed v124 APK. Existing v7 `bf_global_offline_demo_v7` remains untouched. Exact Playwright + signed APK tests prove no `P`, `S`, localStorage mutation.

A future authentic Gem grant requires a proper wallet migration. In current `index.html`, `defaultProgress()` has no Gem field and `parseProgress()` reconstructs a strict allowlist of v7 fields, so **adding `P.gems++` would silently lose balance on reload**. Also `awardDemoRewards()` increments local quest clears on every win. Must implement source-backed first-clear once only, correctly migrate already-cleared v124 progress without duplicating grants or breaking automatic backup/export. Track in Issue #80.

## Verification protocol

Exact v155 feature-head GitHub Actions SUCCESS first; merge only after v154 merged-main Build #532 SUCCESS and clean PR with expected head. After merge require a fresh merged-main full GitHub Actions SUCCESS. No owner APK request until safe on-device migration is warranted.
