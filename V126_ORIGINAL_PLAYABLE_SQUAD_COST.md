# v126 — Original 2022 Global playable squad cost reference

The owner's **verified 2022 Global** `mst-decoded.zip` SHA256 `69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9` contains `unitCost` and `rarity` in `F_UNIT_MST_1/2_Ver1084.json`. This patch joins those exact source fields to **all 72 currently playable** Global forms (six elemental families, twelve forms each).

**Source canonical SHA256** of the 72 JSON-compact tuples `[unitId,unitCost,rarity]`: `ad903ea6923fd71bfd14f50d6bfa566f2391e37a317a053c5236995118a12247`. Family cost sequence in source form order `11–15,21–25,41–42`: `[2,4,8,10,20,3,5,9,14,25,4,6]`. These numbers are source-exact for all six elements and recorded with original rarity.

## Functional scope

- Add an optional in-game **Original 2022 Squad Cost** panel near the live playable squad/leader interface. Report the sum of original `unitCost` values for current *owned* `P.squad` members, resolving their actual `effectiveUnit(baseId)` evolution; each slot shows original unit ID, rarity and cost.
- Avoid pretending the recovered `unitCost` establishes the summoner's **maximum allowed squad cost**. No official 2022 summoner-level-to-cost-cap table was authenticated in the owner's master archive. Show totals only; do **not** enforce restrictions or invent capacity calculations.
- Unknown/evolution-invalid units fail closed and explicitly mark the total incomplete rather than substituting an arbitrary cost.
- No changes to combat, enemies, drops, summons, saved roster, `P.unitExp`, `P.evolutions`, Android package/signing, `P.version===7` or `bf_global_offline_demo_v7`.

## Verification

`test_bf_original_squad_cost_v12600.py`: compares all 72 data rows, authenticated source hashes, independent exact canonical digest, Java load order and 64-KiB asset limit, tests original first-form sum 4, evolved 6★ sum 40, rejects unsupported evolution, confirms v7 `P`/localStorage not mutated in headless Chromium.

This is source-backed squad reference groundwork, not an assertion that original cost-limit gameplay is finished. Future mechanics require a reliable version-specific summoner capacity table and additional source-level validation. CI gating: verify v125 merged-main Build #312 successful; verify exact v126 feature HEAD success; merge only then reverify fresh main CI.