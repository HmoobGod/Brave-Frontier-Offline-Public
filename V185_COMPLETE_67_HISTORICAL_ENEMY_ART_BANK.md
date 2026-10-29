# v185 — Full 67-ID historical BF1 enemy art source-bank coverage

The v182 audit identified **67 distinct source-2014 enemy unit IDs** in 27 archived missions. v183 recovered original archived thumbnails for the 54 not in the existing 127-curated archive. v184 preserved source archival sprite atlases and battle illustration images for those 54. This v185 source-only patch completes the remaining **13 IDs**, whose curated portrait thumbnails were already available.

From the owner's original verified BF1 asset archives we recovered **13 `unit_anime_<id>.png` sprite atlases**, **13 `unit_ills_battle_<id>.png` battle illustrations**, **13 CGG source CSV**, **13 attack CGS**, **13 idle CGS**, and 9 optional movement CGS. All **74 files** are byte-exact archived sources. The new ZIP is 394,697 bytes, SHA256 `81136fa4ba29f7d8a58da3d5583ea10536c6d2ba48d383338d94dfa6b9e5dd3a`, checked in as `source_assets/bf1/BF1_Global_13_Historical_Battle_Visuals_v185.zip.b64`.

The originals are pinned independently:
- BF1_unit_part001.zip SHA256 `c0f03306a4e5efd2513c982ac58b12fff2d72c9ff978b19a839f8932536fc846`
- BF1_unit_part002.zip SHA256 `09f1f3ee682886c3382ac9e3679f2b9d35c056b76d4999913124aa68ca024056`

**Total source bank (v184 + v185): 67 distinct historical enemy IDs, 134 PNG sprite atlases and battle illustrations, plus 240 original animation CSV files — 374 archived source files in all.**

## Do not confuse source art with original 2022 combat

The asset archive is combined historical BF1 data. It is not proven to equal the exact 2022 Global distribution for every unit. And the original 2014 captured battle-wave composition is **not** verified as the original 2022 wave roster. Animations and CSVs have not been deployed; playback interpretation, blend behavior, frame timing, original 2022 enemy AI, drops and damage are **not** established.

This PR adds source-only files, checksums, documentation and tests. No live Android changes, save `bf_global_offline_demo_v7`, recruiting, summons, combat, quests, Gems, Imps, sign-in, signing or internet permissions. `test_bf_complete_67_historical_enemy_art_bank_v18500.py` checks all IDs, 74 new source files, both full original archives, and absence of active Android integration.

**CLAUDE INDEPENDENT REVIEW REQUIRED before any of these archived images/animations are activated in the APK.** First review source-era labels, visual collision with existing sprites, CGG/CGS interpretation, integration as optionally read-only archive preview (not an inferred authentic 2022 battle), save compatibility, browser and signed APK tests. Only then propose an isolated visual candidate with its own CI gate.
