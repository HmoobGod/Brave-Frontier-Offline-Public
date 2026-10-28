# v140 — Five original 2014 Global mission enemy AI source integrations (practice only)

## Exact external sources, independently checked

Five archived `cheahjs/bravefrontier_data` Global mission JSONs were fetched and each Git blob SHA-1 matched to the already pinned v1.20/v2.00 2014 historical wave records:

| 2014 mission ID | Mission | Wave count | Enemy slots | Git blob |
|---|---|---:|---:|---|
| 1 | Basics of Battle | 3 | 4 | `797a2945a40bcfffe7dfc500c8e3dfb6eb81b8fe` |
| 2 | Element & Skill | 3 | 7 | `4b85fcbea4ee41c722b4d54a4140c5d84cd819b0` |
| 10 | Start of Adventure | 5 | 11 | `556829bc0639e417ecd4dbc99ef28c44da25c621` |
| 11 | Monsters of the Prairie | 5 | 9 | `cd089b9640c049b033ef16a6c52e5f3c1d9a3f36` |
| 40 | Shadowy Forests | 5 | 10 | `24da1148c7e8fd2293e504d0fd1b8f0594a6df51` |

Original source has **41/41** exact unit/AI records across **21 waves** with **one attack action per enemy per turn** (`act counts="1~1"`), `attack` selection weight 100%, target condition `random`, type `2`, original parameters `-1`, and empty conditions. All 41 source unit IDs/names/HP/ATK/DEF/AI IDs match the owner repository's 2014 historical data. Their names, source blobs, row order and integer fields are stored in `source_data/bf_global_historical_five_mission_ai_v140.json`.

## Playable integration and provenance

New optional offline JS adapter `bf14000_five_historical_source_ai.js` is loaded **after** the original v87 Basics source reference in Android WebView and validates every mission against v2.00 historical Archive Trials' exact source provenance and all unit/wave rows. It fails closed when missing or mismatched. For any of these five supported missions, live Archive Trials practice selects one original 2014 `attack` decision for each living enemy every enemy reply, with KO'd enemies unable to act. The earlier v139 Basics single-mission adapter remains as fallback, and 16 other historical practice missions retain their prior synthetic enemy action behavior.

**Important limitations:** This confirms **2014 historical attack actions**, NOT native 2022 Global mission encounters or enemy AI. Practice damage (`max(12,ceil(ATK/12))`), Guard mitigation, random target selection (not modeled in practice), player aggregate HP, loot, statuses and rewards remain explicitly synthetic. No main-game quests, existing battle AI, unit growth, experience, drops, currency, evolution or saved user data are altered. Original external data is used as facts; no third-party gameplay code has been copied.

CI tests all 41 enemy slot source joins and 21 source-backed action plans against the original repository historical records; checks native-targeting limitation, KO-filtered turns, mismatches failing closed, basic playable practice activation and exact `P`, live `S` and v7 localStorage before/after; Android APK packaging also gated. Owner installed v124, no APK request until ~v150. v140 branch stacks on v139 and must not be merged until v139 feature-head CI and merged-main CI succeed; v140 needs its own exact-head CI and postmerge main success.
