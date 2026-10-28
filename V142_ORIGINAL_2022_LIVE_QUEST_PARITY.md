# v142 — Full live 2022 Global quest economy and prerequisite parity

## Authentic 2022 Global source, not reconstructed 2014 AI

The owner's original, SHA256-verified 2022 Global `mst-decoded.zip` has SHA256 `69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9`. Its **translated** `F_MISSION_MST_1_Ver1118.json` has SHA256 `d4e364b6c1c5a825c0153c57bdd4123cd35800c74db795d913d119b6c9a99f83`. These values were independently compared to the owner's **actually installed signed v124 APK**.

All **106 live 2022 quest IDs** in the APK match the original 2022 mission master for all seven gameplay-critical scalar fields:
1. missionDungeonId (dungeon association),
2. requiredMissionIds (story quest prerequisite),
3. missionBattleCount (waves),
4. missionEnergyUse,
5. exp,
6. zel,
7. karma.

That is **742/742 exact field comparisons**, across **106 unique playable mission IDs**, with no missing source IDs. It also independently verifies live `awardDemoRewards()` already credits `QUEST.exp`, `QUEST.zel`, and `QUEST.karma`. No replacement or guesswork is necessary for these already-authentic fields. The canonical 106-tuple source SHA256 is `a1b36659dfc80bc6e1e0e244ba52b3c6d423b239cf684439a5488bf679764a66`. The exact records are pinned in `source_data/bf_global_original_2022_live_quest_economy_v142.json`.

## What still is not original

Original 2022 **enemy-wave compositions, enemy AI, drop probabilities, material drops and unit summon/EXP interpolation** remain unverified in the current playable story. The existing `awardDemoRewards()` still explicitly grants extra **DEMO catalysts, summon tokens and training shards**. These are not represented as recovered original 2022 quest rewards. Player `P.level` and unit `demoLevel` are also explicitly demo systems and are not upgraded by v142.

The original scalar reward fields are *already* used for live quest clear, so this revision is **regression protection**, not a new playable content unlock. Future PRs introducing external repositories, new quest content, or reconstructed drops must not regress these verified original fields.

## Tests and save safety

- `test_bf_original_quest_economy_v14200.py`: checks source provenance and 106-tuple digest, parses all live base and appended quests from actual prepared HTML, compares all 742 fields, verifies `awardDemoRewards()` uses original scalar values, runs headless Chromium to check all live quest tuples and unchanged v7 save state.
- `test_bf_packaged_original_quest_economy_v14200.py`: independently reads the signed Android APK and repeats the full 106-quest original scalar parity check; verifies unchanged `bf_global_offline_demo_v7` key.
- The complete test was **locally executed and PASSED** on the owner's verified signed v124 Build #302 APK. The exact new feature branch and merged-main builds still require GitHub Actions success.

No `index.html`, combat script, 72-unit roster, material inventory, quest clear, save schema (`P.version===7`), Android package/signing or player data is changed. This is a safe baseline for subsequent true original Global gameplay restorations.

CI gating: exact v142 feature HEAD success and a successful preceding merged-main build before merge; fresh main CI success before promotion. Installed user v124; next APK planned at v150.
