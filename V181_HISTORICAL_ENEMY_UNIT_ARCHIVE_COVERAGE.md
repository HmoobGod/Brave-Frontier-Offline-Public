# v181 — Historical 2014 enemy IDs versus the original 2022 Global unit catalog

The 27 captured original **2014** Global mission records preserved in v120/v200/v178 contain 168 historical waves and 456 enemy placements. The original **2022** Global unit/form archive already contained in our repo records 2,291 unit IDs and 127 curated unit thumbnails. To inform future sprite/formation restoration, this patch adds a **read-only lookup** between the two archives using their numerical unit IDs.

## What this audit actually establishes

For each original 2014 mission it reports the number of historical enemy placements with an ID present in the catalog of 2022 Global unit/form records, and the subset with a curated **2022 unit thumbnail**. It also reports which unique historical IDs are absent. The result is deterministic and emitted to GitHub Actions stdout as `CROSS_ERA_COVERAGE_REPORT`.

This is strictly **cross-era ID overlap**. A matching ID does NOT prove the 2014 enemy appeared at that position or in that wave in original 2022 battles. A unit thumbnail available from the 2022 archive does NOT prove it is the actual 2022 battlefield sprite. Historical stats, boss AI, skill action conditions, random enemy choices, mimic content, treasure and drops are still unverified for 2022.

## Reproducible source controls

`test_bf_2014_enemy_2022_unit_catalog_coverage_v18100.py` validates the pinned SHA256 of both original unit catalog compressed bytes and uncompressed JSON, checks the 2,291 unique 2022 unit IDs and 127 thumbnails, verifies 27 distinct historical mission IDs/168 waves/456 ordered enemy placements, preserves 2022 source wave-count equality, and counts each archive-ID lookup without changing any assets or saves. No network required: all inputs are already checked in.

**App impact:** None. No JavaScript, Java, Android resource, UI, quest unlock, battle, summon, enemy AI, original reward, save `bf_global_offline_demo_v7`, signing or network permission change. The existing 21 historical practice quests remain 21; the newer six historical captures are research-only.

**CI/merge:** v180 exact-head CI and its merged-main CI must be green first, then v181 feature CI on its exact head, SHA-guarded merge, and merged-main CI. No Claude review required for this source-only coverage report. **Claude review required prior to enabling 2014-derived enemies, AI, drops or assets in any gameplay**, with explicit 2022-versus-2014 authenticity boundaries.
