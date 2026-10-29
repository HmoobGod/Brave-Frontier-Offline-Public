# v180 — 27 historical Global quest wave-count parity audit (data-only)

We now have **27 archived 2014 Global quest snapshots** represented in separate source sets: 4 quests from the v120 capture, 17 quests from the v200 archive lab, and six quests preserved in the v178 read-only source expansion. Collectively, these contain **168 historical waves and 456 ordered enemy slots**. Every mission ID is present in the owner's SHA-pinned **original 2022 Global mission master** from v142, and **every one of the 27 2014 wave counts equals the corresponding original 2022 missionBattleCount**.

This **27/27 parity** is evidence of *quest-stage count continuity only*. It does **not** establish the 2022 Global original battle formations, enemy IDs, wave ordering of opponents, boss scripts, AI actions, drop behavior, rare Mimics, or monster tuning. Original 2014 data remains original 2014 data. No source-based gameplay substitution is authorized by this result.

The new test `test_bf_27_historical_2022_wave_count_parity_v18000.py` reads all 27 archived source files, validates unique IDs and immutable 2014 Git blob identifiers, checks contiguous stage ordering and integer enemy references, compares each stage **count only** against the exact 2022 source master, and verifies the six v178 captures are not loaded into the existing v200 practice panel or Android Java loader. It does not write files or change the app.

Original 2022 source pins:
- `mst-decoded.zip`: SHA256 `69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9`
- `F_MISSION_MST_1_Ver1118.json`: SHA256 `d4e364b6c1c5a825c0153c57bdd4123cd35800c74db795d913d119b6c9a99f83`

Historical sources:
- [cheahjs/bravefrontier_data](https://github.com/cheahjs/bravefrontier_data/tree/master/missions_parsed): captured 2014 Global quest-wave files
- [BluuArc/bfmt-data](https://github.com/BluuArc/bfmt-data/tree/master/gl/mission): independent 2015 quest metadata, reviewed separately in v179

**Release constraints:** This is a research-only regression. No `index.html`, Android Java/JS assets, binary files, save `bf_global_offline_demo_v7`, progression, rewards, Gems, Imps, AI, networking, signing, or source-loader changes. Do not merge ahead of green exact-head CI and all prior merged-main gates.

**Claude review is not needed** for read-only cross-era count checks. **Claude review IS required** before enabling 2014 archived wave rosters, behavior, or any claimed original 2022 native enemy AI in playable battles.
