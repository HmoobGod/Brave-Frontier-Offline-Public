# v184 — Archived BF1 historical enemy battle visual assets recovered

After recovering the 54 missing archived BF1 unit thumbnails in v183, the owner's BF1 asset inventory identified **unit animation atlas PNGs, battle illustration PNGs and native source animation-layout CSVs for all the same 54 unit IDs**.

We retrieved the owner's original unmodified BF1 archive splits from their connected Drive and verified their full SHA256 checksums against the owner's BF1 asset-pack manifest:

- `BF1_unit_part001.zip`: SHA256 `c0f03306a4e5efd2513c982ac58b12fff2d72c9ff978b19a839f8932536fc846`
- `BF1_unit_part002.zip`: SHA256 `09f1f3ee682886c3382ac9e3679f2b9d35c056b76d4999913124aa68ca024056`

Source-only `source_assets/bf1/BF1_Global_54_Historical_Battle_Visuals_v184.zip.b64` contains an outer ZIP (1,722,500 bytes, SHA256 `1c450f3487cbb4ec4c6a7103d35ec5b6680d575de4094c6fc39f0ff4084d9914`). It includes **three nested numbered parts**, each covering 18 original unit IDs with untouched archived filenames and a per-file SHA256 provenance ledger.

Across the three parts there are **300 original archived source files**: **54 `unit_anime_<id>.png` sprite/animation atlases, 54 `unit_ills_battle_<id>.png` battle illustrations**, plus **192 source `unit_cgg_<id>.csv`, `unit_atk_cgs_<id>.csv`, `unit_idle_cgs_<id>.csv` and optionally `unit_move_cgs_<id>.csv`** layouts. All 54 IDs correspond exactly to v183's previously recovered missing-thumbnails set.

## Strict version and mechanics boundary

These are genuine **archived BF1 animation/image resources**. This does not independently prove that the exact same asset revisions appeared in the final **2022 Global** client. In particular, merely finding an image and CGG/CGS layout for a unit ID does **not** establish an original 2022 enemy formation, exact CGG interpretation, attack playback frame timing, enemy AI, drops, or damage rules.

**Nothing is enabled in the Android game.** This PR adds a bundled original art source bank, a parser/checksum/coverage test, docs and a CI invocation only; no Java/JS, Android resources, live quest, unit ownership, player save `bf_global_offline_demo_v7`, rewards, Gems/Imps or permissions/signing changes.

CI: `python test_bf_archived_enemy_battle_visuals_v18400.py` checks both original archive SHA pins, all three internal ZIP SHA pins and their per-file checksums, exactly 54 unique v183-sourced unit IDs, 108 PNGs, 192 CSVs and no 2022-native formation/AI claims.

**Claude review is required before any Android integration or playback of the newly recovered battle assets.** The reviewer should confirm animation frame semantics and combat-facing art orientation, source/version caveat, preservation of manual controls and Auto Battle, save compatibility and fail-closed behavior when an asset/layout is absent. Separate gameplay source evidence remains required to use these sprites as a particular 2022 wave's enemies.
