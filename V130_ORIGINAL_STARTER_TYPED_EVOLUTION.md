# v130 — Source-exact 2022 Global 7★/8★ starter evolution requirements (read-only)

Owner source of truth: `mst-decoded.zip`, SHA256 `69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9`; original `F_UNIT_EVO_MST_Ver597.json`, `F_UNIT_MST_1/2_Ver1084.json`, and `F_ITEM_MST_Ver1027.json`. The 12 7★/8★ starter recipes were independently cross-checked in the already merged v127 manifest `bf_global_2022_starter_7_8_source_readiness_v127.json`.

## Exact recovered mechanics data

Six 6★→7★ starter evolutions each cost **1,500,000 Zel, zero Karma**, and require four original unit materials (`evoMaterialType=1`) plus one separate **original evolution item**, ID **110100**, as `evoMaterialType=2` in source slot 5. Six 7★→8★ starter evolutions each cost **3,000,000 Zel, 1,000,000 Karma** and require seven original unit materials and item 110100 in slot 8. This typed item is not interchangeable with saved `P.materials` counts. The 2022 source item exists as `F_ITEM` ID 110100 (original Japanese title `神越の魂石`). An official 2022 Global English item name, acquisition schedule and original inventory/leveling mechanics are not yet established.

The source-preserved 12 compact rows `[targetId,fromId,rarity,unitCost,maxLevel,Zel,Karma,[[sourceSlot,type,materialId],...]]` have canonical compact SHA256 `a5b91a61b5101f378fcc2692ca97b601c2034cf150c0716e9b561aebc7a0bed6`. Rarity 7 originals cost 38 and max level 120, rarity 8 cost 45 and max level 150.

## Scope and safety

- UI: optional collapsible Units panel showing all 12 original source recipe chains, currencies and individually typed material slots. Pure read-only lookup API `BFGlobalOriginalStarterTypedEvolutionV13000`.
- No side effects to `P.version===7`, saved `bf_global_offline_demo_v7`, roster, player EXP, squad, items, materials, summon mechanics, battle stats, Android package/signing or 72 playable forms.
- **No actual playable 7★/8★ evolutions** yet. Do not infer item acquisition, source-native resource restrictions, 2022 XP thresholds, CGG blend or Omni rules from recipe metadata.
- Automated browser guard: complete source parity across 12 raw 2022 records, prevents mixing type 1 and type 2, verifies original Zel/Karma/type2 item 110100, UI display, `snapshot` read-only eligibility, script idempotency, unchanged `P`/localStorage.

Merge only after v129 merged-main Build #342 SUCCESS and exact v130 feature build SUCCESS; require fresh merged-main GitHub build SUCCESS. The owner is currently installed on v124 and expects no Android upgrade until v150 (absent a critical blocker).
