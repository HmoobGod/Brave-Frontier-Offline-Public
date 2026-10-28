# v135 — External progression extraction audit (DecompFrontier; research only)

## Why this source matters

The open-source [DecompFrontier server](https://github.com/decompfrontier/server), commit `7cc0ebd3be79ca561874f70224c3ed924224583b`, contains two structured candidate datasets that may help eventually replace DEMO player-level and unit EXP progression. The server identifies itself as an **experimental emulator for Brave Frontier client v2.19.6.0**, NOT as the authenticated 2022 Global runtime. Its code license is **AGPL-3.0-or-later**.

Source files and Git blob identities:
- [`deploy/system/user_level.json`](https://github.com/decompfrontier/server/blob/7cc0ebd3be79ca561874f70224c3ed924224583b/deploy/system/user_level.json), blob `32a0510835917dd1a41f360de4ac1c62eda1db60`: **1,000 ordered player-level records**, with an integer level, an experience value, and candidate energy / squad cost / friend-cap fields. The integer roles are inferred from historical examples, not independently verified against native Global 2022 level-up behavior.
- [`deploy/system/unit_exp_pattern.json`](https://github.com/decompfrontier/server/blob/7cc0ebd3be79ca561874f70224c3ed924224583b/deploy/system/unit_exp_pattern.json), blob `c109ff5059f3fad457d95ad196552d601716d4db`: **804 records**, 201 levels each for IDs **10, 15, 20, 25**.

In the candidate player-level dataset, *source-stated* level / candidate XP / energy / squad-cost examples are 1/0/15/100, 2/20/16/102, 10/460/18/117, 20/3685/27/131, 100/57220/96/243, 200/150320/147/310, 1000/1023143/431/844. These are reference **observations**, not the user's actual 2022 Global level-up costs, and **not shipped game rules**.

Candidate unit EXP dataset:
| Pattern ID | Rows | Level 2 | Level 100 | Nonzero rows | Source confidence |
|---|---:|---:|---:|---:|---|
| 10 | 201 | 10 | 25,062 | 200 | Decomp emulator candidate |
| 15 | 201 | 15 | 37,592 | 200 | Decomp emulator candidate |
| 20 | 201 | 21 | 50,123 | 200 | Decomp emulator candidate |
| 25 | 201 | 0 | 0 | **0** | **Do not use** as leveling progression |

The source field named experience is **not** yet proven to represent *incremental XP or cumulative XP* under the original 2022 Global client. Calling it original native EXP without a packet trace or independent original historical comparisons would be speculative.

## Owner 2022 Global cross-check

The owner's independently SHA256-verified original 2022 decoded `mst-decoded.zip` contains **2,291** unit records. Its original `unitExpPatternId` mapping is **10:248 units, 15:245 units, 20:1,798 units**, as pinned in existing v121 CI. The **72 currently playable forms** use only these three IDs. There are **zero** original owner unit forms with pattern 25. Matching an *identifier* does **not** verify the emulator's *numeric XP thresholds*.

The owner's decoded 2022 archive also lacks the original production player-level numeric EXP/capacity tables; original 2022 summoner cost maximum and all unit level XP curves still require independent confirmation. Historical community values can be used for cross-reference, but not as a substitute for original authenticated behavior.

## License + anti-regression boundary

- Do **not** import the AGPL server emulator or copy complete external data tables into the Android app without license review and compatibility decisions. v135 stores only a small sample of factual numerical comparisons, immutable provenance/commit/blob IDs, and independent test code.
- No `P.unitExp`, `P.version===7`, `bf_global_offline_demo_v7`, owner roster, BB effects, combat, item inventory, quest logic, summoner XP, or squad-cost restriction changes.
- No new runtime JavaScript asset or packaged data. This is an independent research gate, deliberately not advertised as new playable progression.
- `test_bf_decomp_progression_candidates_v13500.py` validates the provenance, sample edge cases, 201-row structure, pattern-25 fail-closed policy, original-owner 2,291 / 72 unit pattern joins, existing v7 save key and absence of any v135 runtime injection.

## Actionable next stage

1. Find native client/packet traces or independent original-2022 numerical XP and summoner capacity references to distinguish per-level delta versus cumulative XP and verify unit types.
2. Validate 2022 original level-up/level-cap behavior with deterministic replay against the owner's save format before changing live XP or team limits.
3. For genuine functional acceleration, independently reuse architectural ideas from Godot's offline stage/battle system, not its simplified combat coefficients or incompatible Godot runtime. [Brave Frontier Godot](https://github.com/aMytho/brave-frontier-godot) explicitly describes itself as a *partial, customizable remake*, not complete Global; DecompFrontier's `MissionStart.cpp` and `DeckEdit.cpp` still return `Unsupported`.
4. Prioritize playable 7★/8★ evolution after verified unit rendering, item-material inventory semantics and original skill/evolution costs, **not** a wholesale unverified repository merge.

CI promotion is gated behind completion of v133/v134 prior main builds and exact v135 feature-head success. The user remains on installed v124 until a planned v150 APK.

