# v168 — 2022 original level-one Lord base stats in archive DEMO battles

**Baseline:** v167 main SHA `f52254b437d64417911646f232d4c26ecdaeef35`, original v167 feature Actions Build #590 SUCCESS (198/198). Fresh merged-main v167 Build #591 run `40712322118` must finish SUCCESS before v168 can merge.

## Authentic source

The verified original owner's 2022 Global master archive `mst-decoded.zip` SHA256 `69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9` has 72 playable `F_UNIT_MST_1/2_Ver1084.json` records. Existing `source_data/bf_global_2022_playable_lord_stat_endpoints_v116.json`, `bf11600_original_lord_stats_data.js` and `bf11600_original_lord_stats_reference.js` already check all forms, exact `base.hp/atk/def/rec`, `maxLevel`, and `lordAtMax`. Previous v116 only displayed these endpoints, and v115 caps only source-verified maximum unit levels.

## Precisely scoped combat change

- In the existing `playerUnit(i)` bridge, **after** v115 original-level cap and **before** v111 existing original leader ATK/HP bonuses, call `BFGlobalOriginalLevelOneLordV16800.apply(unit,i)` only if that optional source gate is loaded.
- Require archive DEMO mode, legit owned/selected/effective unit ID, exact source endpoint at `level===1`, **strictly zero** persisted per-unit EXP (`P.unitExp[baseId]??0===0`), and the untouched original DEMO constructor fields before applying.
- Update **only** in-memory newly constructed unit HP/maxHP/ATK/DEF/REC to original 2022 base values (not level-up, player roster or saved state). Existing source original ATK/HP leader percentages stack once afterward using v111.
- Unknown or malformed records, unowned/mismatched units, positive EXP, intermediate levels and training fail closed with the previous DEMO builder. Source-backed Lv1 base values do **not** prove native 2022 unit-type roll or the precise original EXP progression.
- Show a plainly labeled original-source level-one party overview; `P.version===7`, canonical save key `bf_global_offline_demo_v7`, Android package/signing, original progression, 106 playable quests, Amdahl source-only missions, 7★+ restrictions and player saves are unchanged.

## Regression gates

`test_bf_original_level_one_lord_combat_v16800.py` uses prepared Chromium HTML to cross-check all 72 original source endpoints, exercise 18 base starter forms across six elements, prove source leader +25% ATK stacking after the exact base, verify zero-EXP gate, disallow other-level interpolation, verify training and reload idempotence and v7 state isolation. `test_bf_packaged_original_level_one_lord_combat_v16800.py` checks signed APK presence, v116 source module load order, the canonical save key, live source guard and Android identity.

**No claimed full native battle reconstruction:** exact original damage formula, unit-type rolls, native intermediate stats/rounding, original EXP patterns and authentic 2022 enemy formations/AI remain unverified.

**Merge policy:** require fresh v167 merged-main #591 SUCCESS, v168 exact feature-head CI SUCCESS, SHA-guarded PR merge and fresh merged-main CI SUCCESS before v168 is declared stable. User remains on device v124 until explicit update request.
