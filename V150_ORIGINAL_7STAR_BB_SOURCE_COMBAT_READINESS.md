# v150 — original 2022 Global six-element 7★ Brave Burst source combat readiness

This checkpoint adds **verified original skill records and a non-saving combat regression**, not playable 7★ evolution or native damage reconstruction. The user still has installed v124 and intends to install the next APK at v150 after all required merges/build checks.

## Independent 2022 original source

The owner's SHA256-verified `mst-decoded.zip` (`69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9`) has `F_SKILL_MST_1_Ver1535.json` and `F_SKILL_LEVEL_MST_1_Ver1487.json` records for the exact six 7★ starter BBs `10016`, `20016`, `30016`, `40016`, `50016`, `60016`. Full source file SHA256s are pinned in `source_data/bf_global_2022_sevenstar_starter_bb_v150.json`; exact source tuple digest (six source effect-frame strings, first attack damage groups, complete 10-level strings and target/type fields) is `f1f47eacbddef11dd724737f6e1669de2c16e42a2cf9ab8bd6f3bd09f0f4ba64`.

All six BBs have original `skillTypeId=1`, `targetType=2`, `skillTargetArea=2`, and a **single source damage frame group** weighted to **100%**. There are **71 original BB hit events**, in the six sets of **12, 12, 12, 12, 13, 10**. Source skill level 1 is `2500:150,80,0,0,0,0`; level 10 is `2500:250,80,0,0,0,0`. Original source metadata is preserved losslessly. This does not prove the original damage multiplier or native hit timing.

## Runnable isolated combat verification

`test_bf_original_sevenstar_bb_combat_v15000.py` loads the exact unchanged **production Android HTML into a throwaway Chromium browser page**, then inserts six source BB scope/power records **only into the test page's in-memory HTML string**. Each 7★ starter is temporarily registered for one attack against two high-HP test dummies, using the original source event timelines and all-enemy targeting through the existing DEMO combat engine. The source first parameter 150 is interpreted by the existing DEMO engine as 2.5× for **test purposes only**—this is explicitly not validated as original 2022 damage. The test asserts all enemies are hit, the source event groups contain exactly 100% weighting, source forms are unregistered after the test, the normal 72 playable unit forms are untouched, and `P.version===7`, `P` and `bf_global_offline_demo_v7` bytes never change.

The source metadata and test code do not install a 7★ unit in user-owned roster, grant Legend Stone items, spend evolution materials, change BB animations, award rewards, alter any saved data or modify production `index.html`. No native runtime skill, hit-clock, enemy AI, damage/DEF, SBB/UBB/LS, 7★ growth, true RNG or original animation compositor is claimed. The production APK is unchanged except for retaining the normal preexisting source-data/test files, which are not packaged as player gameplay.

## Verification gates and next actual gameplay milestone

Local test executed against the packaged game HTML from v126: **PASS, six all-enemy 7★ original BB event groups, 71 source hits, unchanged 72 units and v7 saves**. CI runs the same against the exact newer prepared source tree, after all existing v148 tests. Merge only after v144–v149 prerequisites and their exact-head and merged-main builds succeed; v150 needs its own exact-head CI and a new merged-main CI success before any APK is supplied to the owner. The next playable step requires authentic source sprite transforms, 7★ evolution item inventory, source level/EXP growth and native BB damage mechanics; test-only actors cannot be represented as unlocked units.
