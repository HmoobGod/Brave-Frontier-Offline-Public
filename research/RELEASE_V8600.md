# Brave Frontier Global v86.00 — Source SBB and UBB Crystal Check Coverage

**Verified parent:** v85.00 Build #322, commit `9717fb25fa12e333d49392556a210bc7123dfb9d` (GitHub Actions signed APK artifact #12590790370).

The 2022 Global `F_UNIT_MST_1/2_Ver1084.json` and nine `F_SKILL_MST_*_Ver1535.json` parts yield **1,290 uniquely joined SBB skills** and **932 UBB skills** across the 2,258 validated normal-attack collectible unit forms. Exact source per-skill `dropCheckCount` values are preserved in a lossless compact table with two independent FNV checksums.

- **SBB:** 1,282 complex/multi-group skill frames cannot establish a native total hit count; 7 simple offensive enemy-target damage groups have weight sum 100 and permit bounded *per-target reference* crystal calculations; 1 simple nonoffensive effect is excluded from rolls.
- **UBB:** 931 complex/multi-group and 1 simple nonoffensive effect; **zero** skills safely support calculated BC event totals. This release intentionally does not simulate original UBB crystal production.
- All original v83 SBB source records are cross-checked, including unit #60025 skill #160025 with `dropCheckCount` 25 and one simple offensive event.

`BFGlobalAllSBBUBBDropChecksV8600` is a read-only archive-linked reference, not a gameplay implementation. It never spawns/collects crystals, modifies HP or BB, awards loot, changes enemy AI, uses online services or writes saves. Original target multiplicity, per-enemy resistances, split group damage timing and pickups remain unknown. Preserve all v7 saves, package ID, debug signing and pre-existing battle demo behavior. Only promote on full CI success with uploaded signed APK artifact.