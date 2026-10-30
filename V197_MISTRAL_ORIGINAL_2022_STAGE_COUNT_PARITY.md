# v197 — 34 original 2022 vs historical 2021 Mistral battle-stage counts

**Research only.** The project's pinned 2021 extracted Mistral records match the owner's actual original 2022 Global `missionBattleCount` in **all 34 of 34 missions**. This extends the earlier 27/27 cross-era comparison (v180) with a different 2021 snapshot and confirms battle-stage *counts*, not the opponents inside those stages.

## Evidence and provenance

- Original 2022 Global archive: `mst-decoded.zip` SHA-256 `69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9`; mission master `F_MISSION_MST_1_Ver1118.json` SHA-256 `d4e364b6c1c5a825c0153c57bdd4123cd35800c74db795d913d119b6c9a99f83`.
- Authenticated original 2022 mission-stage counts: existing, source-pinned `source_data/bf_global_original_2022_live_quest_economy_v142.json` (106 original mission records). Repository Git blob `9e9e98791d5a1ba04cdc095cf21fd46dfe5091fe`.
- Historical 2021 `cheahjs/bravefrontier_data/missions.json` commit `7be4ee5ade8023580c83563fb306eb4e2b747256`, Git blob `750871aa060478cc674e7d3e02c739f26364ef8e`. Existing 34-row curated fixture `source_data/bf_global_2021_mistral_mimic_history_v196.json` Git blob `321f0f8a2dec81340e23b0069b8f00e5783c9c57`.
- Exact original 2022 raw encounter/mimic strings: existing `source_data/bf_global_mistral_raw_mission_evidence_v056.json`, repository Git blob `87fe678b1fe70a041212fdf9050dfa4003072312`. Numeric encounter-looking strings remain **opaque**.
- The three committed research fixtures are each anchored to their exact Git blob bytes, and their source-record metadata and matching 34 IDs are checked before comparing counts.

## Findings

- **34/34** 2021 historical `old2021BattleCount` values match the source-verified original 2022 `missionBattleCount`, with zero discrepancies.
- Examples: mission 1 has 3 stages; mission 12 has 6; mission 60 has 6; mission 63 has 7; mission 85 has 8. All use 2022 values, independently matched to 2021.
- Prior v196 mimic-token classes are still **21 empty / 13 candidate**; this v197 audit does not interpret 2022 Mimic percentages or placements.
- No 2022 enemy identities, formations, stage-to-opponent mappings, attack scripts, drop rates or original Mimic spawn timing are authenticated by stage-count continuity.

## Implementation and safety gates

- `audit_bf_mistral_stage_counts_v19700.py` performs a strict read-only three-source join and emits an optional deterministic JSON report **outside the repository only**.
- `test_bf_mistral_stage_counts_v19700.py` tests all 34 exact IDs, 2022 stage-count examples, 10 negative corruption/provenance probes, report reproducibility, blocked repository output and byte-for-byte preservation of original input files and live `index.html`.
- The existing GitHub Actions workflow runs the new test after v196. No Java, Android APK assets, original DEMO quest waves, enemy AI, `P.unitExp`, v7 saves, gems, imps, settings or signing changes.
- Merge only after successful v196 merged-`main` CI and v197 exact-head feature CI, followed by a successful new merged-`main` build. Android device testing remains required for any later game-facing update.

**Next blocker:** Obtain a version-authenticated 2022 enemy-group/encounter definition or original client/parser semantics for opaque mission references before implementing native enemy placements and combat. Do not silently use 2021/2014 enemy rosters as if original 2022.
