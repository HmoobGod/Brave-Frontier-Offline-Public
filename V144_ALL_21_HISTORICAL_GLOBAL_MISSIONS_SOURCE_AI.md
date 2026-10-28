# v144 — all 21 archived 2014 Global missions have source-classified enemy actions

## Independently verified external source extraction

This continuation of v139–v141 examines **all remaining 12 historical Global 2014 missions**, pinned against original `cheahjs/bravefrontier_data` parsed mission JSON Git blob identities and the owner's existing `v2.00` 2014 mission roster. The exact original per-wave enemy unit ID, name, HP, ATK, DEF, AI ID, action-count range, all action types/parameters/weights/target conditions/target types, and number of action-condition parameters were extracted and preserved in two source JSON files.

| Original source subset | Missions | Waves | Enemy slots | One normal attack | Complex AI |
|---|---:|---:|---:|---:|---:|
| v144 original archive IDs 41,42,50,51,52,60 | 6 | 31 | 82 | 73 | 9 |
| v144 original archive IDs 61,70,71,200,202,240 | 6 | 40 | 95 | 75 | 20 |
| **New v144 extraction** | **12** | **71** | **177** | **148** | **29** |
| Prior v139–v140 source subset | 5 | 21 | 41 | 41 | 0 |
| Prior v141 four mixed source missions | 4 | 20 | 46 | 40 | 6 |
| **Full historical v2.00 practice source coverage** | **21** | **112** | **264** | **229** | **35** |

Source names and original Git blob IDs are preserved in `source_data/bf_global_historical_remaining_ai_v144_part_{a,b}.json`, together with all 177 original per-enemy attack/skill/turn-end selection records and complete metadata.

## Actual functionality in isolated historical practice

`bf14400_remaining_historical_source_ai.js` contains a compact (under Android's 64-KiB single-file limit) **source-backed 177-enemy action lookup**. It validates every one of the 71 source waves, all 177 enemy slot identities and source Git blob identities against the game's existing history dataset before activating. In the existing optional Archive Trials practice, **148 enemy decisions** are recognized as original 2014 one-attack-per-living-foe, 100%-weighted and random-target source choices. **29 complex enemy decisions** are explicitly labeled `UNMODELED COMPLEX AI (synthetic reply)` and continue to use the prior synthetic fallback. Defeated enemies never act. Original 2014 conditions, multiple actions, skills, targeting RNG and skill priority are **not fabricated**.

All 21 historical practice missions are now evidence-classified. This is a complete audit of the included **2014 archive subset only**, **not** a reconstruction of original 2022 Global enemy behavior, combat damage, targeting, rewards or mission spawns. We have not copied external third-party code: only historical source facts were independently re-implemented in our sandbox practice.

## Safety and evidence

Separate Chromium regression independently verifies all 177 source slots against the owner repo's historical v200 mission records, recomputes the 148/29 classification from original action fields, checks all mission/wave plans, KO and mismatched source fail-closed behavior, and compares entire `P` owner state, `S` live battle state and `bf_global_offline_demo_v7` saved storage before and after the historical practice. Signed APK regression verifies the offline optional JS module is actually packaged. No owner unit, XP, BB, quest-clear counter, drop, resource economy, camera, sprites, Android signing, or save format changes.

**Upgrade gate:** v144 branch stacks on v141 verified feature HEAD, and v141 stacks on v140/v139. Do not merge this branch before exact v139–v143 feature and their sequential fresh-main builds pass; afterward verify v144 exact feature-head GitHub Actions and fresh merged-main build before promoting stable. The user's installed APK remains **v124** and next expected user installation is **v150**.
