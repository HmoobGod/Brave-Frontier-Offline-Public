# v127 — exact 2022 Global 7★ / 8★ starter source readiness (12 units)

## Why this matters

The currently installed v124 game and the latest verified v125/v126 development builds have **72 playable Global forms**; the full 2,291-record original Global archive is currently **read-only**. This patch prepares a narrowly scoped expansion for the next twelve historical forms, following the **six original Global starter lines**:

- 7★ IDs `10016,20016,30016,40016,50016,60016`. Original rarity 7, unitCost 38, maxLv 120.
- 8★ IDs `10017,20017,30017,40017,50017,60017`. Original rarity 8, unitCost 45, maxLv 150.

Source recovery: owner's original 2022 `mst-decoded.zip`, SHA256 `69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9`; translated `F_UNIT_MST_1/2_Ver1084.json` plus `F_UNIT_EVO_MST_Ver597.json`. The 12 exact source rows pin base / max-Lord stats, exp pattern ID, original LS/BB/SBB/UBB pointers, original typed/material-counted evolution recipes, Zel/Karma costs and six original image/CGG/CGS asset checksums for each form.

Original source sprite files were extracted without modification from the owner's Drive BF1 asset packs:
- `BF1_unit_part001.zip` SHA256 `c0f03306a4e5efd2513c982ac58b12fff2d72c9ff978b19a839f8932536fc846`.
- `BF1_unit_part007.zip` SHA256 `ad937083a4d023228f8796d45e5edd6adaf575872270476be994121941db3556`.

Verified **72/72 asset files** (anime sheet, thumbnail, original CGG frame geometry, idle/attack/move CGS each). All 12 original CGG files contain nontrivial or unknown orientation, reserved, scale and transform fields; examples include scale zero and orientation code 3. Simply pasting source sprites into existing DEMO renderer **would not establish authentic animation**. The original 7★/8★ levels 120/150 additionally exceed existing playable caps and have unverified native EXP/stat interpolation and 8★ Omni behavior.

An independently extracted source-only compact ZIP has 72 files + the original-source manifest, 1,792,687 bytes, SHA256 `59e81dc4260874cebbf2d79cdadb570f279a5af02762f89633275fb67e45d2f3`. It is stored as a **handoff artifact**, not as an APK-bundled asset. Do not claim the repository's source manifest alone contains the original PNG/CGG/CGS byte payload.

## What this revision does—and does not do

- Add `source_data/bf_global_2022_starter_7_8_source_readiness_v127.json` with independently verified source IDs, stats, material-type-aware recipes and sprite hashes. Exact canonical sorted twelve-unit source tuple digest `dcd3fb0f3d57b44880088f42c87409e3588a24a183ec866095ea0dbeae57bcbd`.
- Add `test_bf_original_starter_7_8_source_v12700.py`, comparing all 12 unit stat/cost records to the packaged original 2,291-record Global archive, enforcing the 72 files/source hashes and asserting unknown CGG transform semantics are flagged as unverified; Chromium checks 18 starter +54 evolved **existing** playable forms and unchanged save v7.
- **No new playable 7★/8★ forms yet.** Preserve existing animation, unit ownership, quest rewards, original/DEMO boundary, Android package/signing, `P.version===7`, save key `bf_global_offline_demo_v7`, `P.unitExp`, `P.evolutions` and current 72 playable unit count.

## Next authentic-gameplay milestone

Determine safe rendering behavior for non-default CGG transform codes and validate original 7★/8★ BB/LS effects and special typed evolution materials. After source-backed CGG/CGS and recipes pass, implement selected **actual playable** 7★ steps incrementally with full offline Android gameplay tests, adapting the existing v115/v124 72-form guarantees consciously. Do not alter all existing accounts or auto-upgrade saved units.

Verification protocol: exact feature-head CI SUCCESS, verify merged v126 main Build #320 SUCCESS, merge, fresh main CI SUCCESS before promoting v127. User stays installed on v124 and doesn't want a new APK until v150.
