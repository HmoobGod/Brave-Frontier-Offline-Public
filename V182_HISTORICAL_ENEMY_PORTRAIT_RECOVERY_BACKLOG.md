# v182 — Original Global historical enemy portrait-recovery backlog

After v181's exact-head Build #773 passed, the research report confirmed **all 67 distinct historical 2014 enemy IDs occur in the owner's preserved 2022 Global unit catalog (2,291 records)**. The curated **2022 UNIT PORTRAIT** subset covers only 13 of those IDs, corresponding to 104 of 456 historical 2014 enemy placements. The remaining **54 IDs / 352 historical placements** do not yet have those particular portrait thumbnails in the curated archive.

To make art acquisition actionable, v182 produces a sorted JSON backlog for all 54 missing IDs with source 2022 unit catalog name (when available), ID, number of observed historical placements, affected missions and wave count, and a *candidate* `unit_ills_thum_<id>.png` thumbnail filename. Highest-frequency missing portraits come first. The filename is an archive lookup hint, **not proof that a file already exists**. No images are manufactured or imported.

Run `python test_bf_original_enemy_portrait_recovery_v18200.py`; it creates exactly one machine-readable report under `source_audit_reports/BraveFrontier-v182-historical-enemy-portrait-backlog.json`. CI attaches this file as a distinct downloadable GitHub Actions artifact `BraveFrontier-v182-original-portrait-backlog`, **not inside the Android APK**. Verifies source SHA256 against the pinned original 2022 archive, validates 27 historical 2014 missions / 168 waves / 456 placements, detects 67 unique ID matches, preserves 13/54 portrait coverage and 104/352 placement counts.

## Source and mechanics protection

All historical enemy wave order, stats and AI belong to **2014-era captures**. Their IDs matching 2022 units and their quest counts being stable **does not** establish original 2022 enemies, spawn locations, battle animation assets, drop rates, sprites, AI or native combat. Portrait thumbnails are **not battlefield sprites**. The optional 21-mission v200 practice lab remains unchanged. A separate authenticated 2022 wave/battle sprite reference is required before gameplay promotion.

This report changes no original app mechanics, Java or JS source, Android resource, user save `bf_global_offline_demo_v7`, inventory, Gems/Imps, battle behavior, enemy AI, summons, loot, permissions or Android signing.

**CI gates:** Wait for v181 merged-main successful CI before merging v182, verify exact-head feature CI and merged-main CI. No Claude review for data-only image recovery inventory. **Claude review is required before promoting historical art, enemy teams or AI into playable combat.**
