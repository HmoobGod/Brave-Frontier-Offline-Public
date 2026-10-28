# v136 — Original 2022 Global Omni upgrade prerequisites (not activated)

The owner's original, SHA256-verified `mst-decoded.zip` (SHA256 `69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9`) includes three authentic original Omni upgrade master tables:

| Source file | Original 2022 records | Meaning, directly represented in source |
|---|---:|---|
| `F_UNIT_EVO_OMNI_MST_Ver94.json` | **18** | Additional stat and SP bonuses by Omni level / unit cost |
| `F_UNIT_EVO_OMNI_RECIPE_MST_Ver95.json` | **70** | Typed upgrade materials by level, unit cost and chosen method |
| `F_UNIT_EVO_OMNI_TYPE_MST_Ver95.json` | **36** | Zel and Karma upgrade costs by method / level / unit cost |

All records are losslessly reduced to numeric tuples and exactly source-hashed in `source_data/bf_global_2022_omni_prerequisites_v136.json`, canonical compact table SHA256 `c9434f360bb0e35edce2182c145f2e99e4e32c60bc9b446606a0d04d42a7a27b`. **There is no external-license uncertainty here**: these tables come from the owner's own original 2022 archive, not DecompFrontier or another emulator.

## Key playable-game findings

- The 18 source bonus records cover **six original unit cost tiers** `45,47,48,50,54,60`, each with source Omni levels `1,2,3`.
- The 70 original upgrade recipe entries are explicitly typed: **18 `ELE_SHARD`**, **34 `ITEM`**, **18 `DUPLICATE`**. The ELE_SHARD entries reference six original shard item IDs `800901–800906`; ITEM rows require `800907` or `800908`; DUPLICATE entries reference material ID 0 with source count 1. All non-duplicate source item IDs were validated against all **1,668** records in original `F_ITEM_MST_Ver1027.json`.
- Original upgrade method `1` uses element-shard/item requirements; method `2` uses duplicates plus, where specified, distinct items. Both methods have their own Zel/Karma source row in the 36-row cost table. The exact UI behavior and original 2022 player inventory/summoner-state representation remain unverified.
- The archived six original 8★ starter forms `10017,20017,30017,40017,50017,60017` all have source **unitCost 45**, confirmed independently from v127 and the 2,291-unit 2022 Global catalog. This gives an authenticated join into the cost-45 Omni table. These 8★ forms are **still not unlocked** in the current playable roster.

## Critical boundaries

This version **does not activate Omni** or modify Android assets. No new playable units, item/shard/duplicate material inventory serialization, Zel spending, stat bonuses, BB/UBB effects, level cap, party cost enforcement, summoner XP, combat, `P.unitExp`, `P.version===7` or `bf_global_offline_demo_v7` save migration.

The fields `DUPLICATE`, `ELE_SHARD`, `ITEM` are authentic source types. Don't convert these into the existing DEMO unit-material count store or grant free resource balances. Implement a separate, tested, save-compatible inventory mechanism only after authentic acquisition methods are established.

`test_bf_original_omni_prerequisites_v13600.py` independently guards 18+70+36 original tables, method/material joins, stat/recipe SHA256s, six original 8★ starter IDs/costs and unchanged Android entrypoint/save state.

## Scope & next gate

The v135 research audit covers DecompFrontier's **external emulator** player-level / unit-EXP candidate tables. This v136 source evidence is from the **original 2022 Global masters** and is stronger, but it alone cannot deliver playable 8★ forms. Prioritize independent verification of 7★ unit leveling, original 8★ visual rendering, owned-item accounting and source-backed BB/UBB effects, then implement one family at a time with deterministic save replay.

Branch `feature/v136-original-2022-omni-prerequisites` is stacked on v135 candidate audit; merge only after verified v133, v134, v135 main builds and exact feature CI SUCCESS. Next owner APK requested around v150, installed owner version remains v124.
