# v172 — Exact original 2022 Lord stat endpoints at source max level

## Source and scope

Baseline: v171 PR #98 feature head `59311d5af3127815dc4756bc6ce3164cfcc1612b` (pending GitHub Actions #663 and independent review of N1/N3 follow-ups), plus v170 merged-main `b387598e54c23ed88077e7db60fb609bfe6ae447`, Build #658 SUCCESS.

The original owner-provided `mst-decoded.zip` SHA256 `69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9` contains verified `F_UNIT_MST_1/2_Ver1084.json` base/Lord maximum stat endpoints and unit maximum levels. Existing `bf11600_original_lord_stats_reference.js` checks 72 playable form records and provides `endpoint(id, maxLevel)` with exact HP, ATK, DEF and REC. This patch **does not invent intermediate level growth or EXP patterns**.

## Precise gameplay change

In `playerUnit(i)` (the existing v111 wrapper) apply `BFGlobalOriginalMaxLevelLordV17200?.apply?.(unit,i)` after original v115 level cap and v168 zero-EXP Lv1 Lord endpoint, and before v169/v171 optional Imp effects and the original v111 leader percentages.

The v172 max-level module applies only if ALL of the following are true:

- Archive demo mode; active, newly constructed, owned, source-qualified playable form selected in the matching squad slot; level equals source exact `unitMaxLevel`.
- Existing demo EXP function reaches the source max level. The demo EXP curve is **not** claimed authentic.
- Current constructed HP/ATK/DEF/REC match exactly the preexisting DEMO linear progression at the source cap. Unexpected builders or modified stats fail closed, not overwritten.
- Source `BFGlobalOriginalLordStatsV11600.endpoint(id,maxLevel)` verifies the exact original Lord maximum stats, alongside source cap and form ID matches.
- Modification is in memory for that one newly built battle actor only, then leader and optional Imp bonuses use their previously established order. Training, Lv1, intermediate levels, unit type rolls, saved EXP, party roster and all v7 keys remain unchanged.

## Tests

- `test_bf_original_max_level_lord_combat_v17200.py` runs Chromium with actual patched page; checks all 72 exact source max endpoints, multiple owned forms at source cap reached using the **existing demo EXP**, source leader stacking order, idempotence, Lv1 and intermediate-level exclusion, training unchanged and save isolation.
- `test_bf_packaged_original_max_level_lord_combat_v17200.py` verifies the exact packaged APK asset, loaded Java bridge order, canonical Gem/Imp save preservation, package ID/signing key identity and no INTERNET permission.
- GitHub Actions performs JS syntax check, Chromium source-bound regression and signed APK packaged regression.

## Release and review

This is one incremental original-source endpoint, not a claim of full original 2022 combat progression. Unrecovered: native EXP thresholds, intermediate stat formula and rounding, non-Lord type generation, enemy formations/AI and native damage calculation.

The v172 PR is stacked on pending v171 PR #98, so **do not merge v172 until v171 is reviewed, exact-head CI SUCCESS, SHA-guarded merge, and the subsequent merged-main CI SUCCESS**. Then rebase/retarget v172, require new exact-head CI and merge-main CI. User-installed Android v124/save is untouched. Request Claude to independently inspect source gate, max-vs-DEMO level distinction, stat/bonus ordering and regressions before merging.
