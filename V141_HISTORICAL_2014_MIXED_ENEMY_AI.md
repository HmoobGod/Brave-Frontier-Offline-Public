# v141 — Preserve complex source AI while executing 40 additional historical 2014 normal attacks

This is another **historical 2014-only** extraction from the original `cheahjs/bravefrontier_data` parsed Global mission archive, **not** authenticated 2022 Global AI. Four exact source Git blob SHAs are pinned and verified against v1.20/v2.00 historical mission rosters.

| Mission | ID | AI slots | Source-normal | Conditional / complex |
|---|---:|---:|---:|---:|
| Cave of Dancing Flames | 20 | 11 | 9 | 2 |
| Wielder of the Fire | 21 | 14 | 13 | 1 |
| Breath Freezing Snowfields | 30 | 11 | 10 | 1 |
| Manipulator of the Water | 31 | 10 | 8 | 2 |
| **Total** | | **46** | **40** | **6** |

The 40 simple slots are source-authenticated **one normal `attack` per turn** with original percent weight 100%, target condition random, type 2, and no conditions. Six exceptions have source `1~2` action counts or weighted `weakness`/`hp_max` conditional attack/skill/turn_end behavior. These are preserved losslessly in `source_data/bf_global_historical_mixed_ai_v141.json`, but the **source action priority and targeting are not invented or executed**.

The independently authored offline `bf14100_mixed_historical_source_ai.js` adapter joins each slot against the existing v200 historical practice source by mission path, immutable Git SHA, wave, slot, unit ID/name/stats/AI ID. Only validated simple 2014 attacks are described as source-backed; complex enemies retain the previous synthetic volley calculation and are **visibly labeled “UNMODELED COMPLEX AI (synthetic reply)”** when the optional historical practice runs. All enemy damage, player target RNG and real 2022 encounters remain synthetic/unchanged. Fail-closed if mismatched/unknown, 16 other optional historical practice missions retain previous behavior.

Independent Chromium gates validate all 46 original source joins, 40 source-backed versus six complex fallbacks, KO'd enemy filtering, rejected corrupted AI records, and player `P`, live combat `S`, plus localStorage v7 save before/after. Android packaged asset is separately verified. No network, third-party code copied, real player rewards, item inventory, summon, damage/BB, migration, Android signing or unit count changed.

CI: v141 branch stacks upon v140 PR #55, itself stacked upon v139 PR #54. Require exact successful feature-head builds and successful fresh main builds in order; never merge an unverified PR. Owner stays installed on v124, next APK around v150.
