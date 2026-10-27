# v128 — Original 2022 Global 7★/8★ starter CGG/CGS source sequences

## Scope and provenance

This revision introduces the **complete original numeric animation-geometry source** for twelve 7★/8★ Global starters (`10016/17` through `60016/17`), extracted from the owner's SHA256-verified `BF1_unit_part001.zip` and original `mst-decoded.zip` 2022 F_UNIT masters. The original 72 image/CGG/CGS source-file hashes are separately pinned in v127; no source pixel/image files are added in v128.

CSV files `content/unit/cgg/unit_cgg_<id>.csv` and `content/unit/cgs/unit_{idle,atk,move}_cgs_<id>.csv` have been parsed losslessly to signed integer arrays, preserving original CGG frame/layer order and all **eleven fields** per part, plus original four-column CGS sequence values. The twelve records total **308 original composition frames** and **5,378 source layers**. The 184,101-byte normalized array is gzip-compressed to 22,994 bytes and embedded into a 33,971-byte static offline WebView JavaScript resource, under the 64-KiB per-asset reader limit.

Source array SHA256: `7535ec0bae51fe425fc8db7ee3341d0dda0b6e80d6586c88cd888161c4f0951a`; compressed bytes SHA256: `b0f3a29cbec8640b70a1ee0d77512d1f966f473840ec2c9002df9f108a60b976`. They are independently checked by `test_bf_original_starter_cgg_cgs_v12800.py` and `source_data/bf_global_2022_starter_cgg_geometry_v128.json`.

## CGG field semantics and limits

A community BF1 animation engine, [BluuArc/BFFrameAnimator `src/Frame.java`](https://github.com/BluuArc/BFFrameAnimator/blob/master/src/Frame.java), authored by Joshua Castor in 2016, labels each eleven-field CGG layer as x/y, flip (0–3), blend (0/1), opacity percent (0–100), rotation degrees (-180/-90/0/90/180), sprite source x/y, width/height, sheet page. This **corrects the provisional previous assumption** that CGG column 5 was scale; it is opacity per the community renderer. It is not independently verified as native-2022 pixel compositing. The source preserves **zero-opacity** parts exactly; it never interprets them as zero-size sprites.

The original CSV data indicates all 5,378 layers use image sheet page 0. Original rotation, flips and blending are source-preserved and validated; native clipping, additive blend calculation, alpha/raster operations, animation scheduling and 2022 mobile CGG engine equivalence remain unproven. The project does not silently substitute a simulated sprite renderer for original behavior.

## Functional change

- Add offline `BFGlobalOriginalStarterCggV12800.ready`, `lookup(id)`, `count` and `source` returning immutable source geometry/idle/attack/move sequences for exactly twelve original archived forms, with fail-closed invalid/unsupported decompression and row guards.
- Android WebView loads the optional source reader; the **read-only Unit Encyclopedia** displays historical CGG/CGS composition frames and raw attack sequence steps, not a playable sprite.
- Source remains detached from `BF_EVOLVED_UNITS`, `EVO_RECIPES`, battle damage/AI, player EXP, inventory, squad, summons, and offline save keys. No 7★/8★ has been made playable.
- `test_bf_original_starter_cgg_cgs_v12800.py` checks the exact immutable sources, all 308 frame rows / 5,378 layer tuples, original v127 unit joins, source transform ranges, browser decompression, archive UI, and unchanged `P.version===7`, `bf_global_offline_demo_v7` and player progress.

## Next milestone

Render **original-source image geometry** in a bounded proof-of-concept, compare sourced CGG/CGS timeline frames with historical visual evidence, then incrementally make the first 7★ starter playable after validating evolution material typing, levels above 100, BB/LS and save compatibility. Do not advance any owner's saved unit automatically. Original-game fidelity takes precedence over demo QoL.

**Verification:** require v127 merged-main GitHub Actions Build #326 SUCCESS, exact v128 feature-head CI SUCCESS, then merge PR and require fresh merged-main CI SUCCESS. The owner's installed version remains v124, next requested APK update around v150.
