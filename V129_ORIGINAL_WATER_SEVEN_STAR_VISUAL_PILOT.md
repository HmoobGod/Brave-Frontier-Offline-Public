# v129 — 7★ Water source-art reconstruction pilot, read-only

This patch adds a **visual source reconstruction pilot** for the original 2022 Global 7★ Water starter, unit **20016**, not a playable unit and not a full native sprite engine.

## Provenance

- The owner's original Global BF1 archive provides the exact PNG anime sheet, original thumbnail, one CGG layer-composition CSV and three CGS original animation CSVs, all six with SHA256 pinned in the v127 source manifest.
- The exact extracted six-file pilot ZIP (stored base64 for the offline build) has SHA256 `0e23e955e2f7548000c6891f1718c9773d8f459a1aef165b1b34d8c772bae33d`. The original 7★ source geometry also appears in v128's twelve-form CGG/CGS decoder.
- The build-time Pillow renderer converts the original 23 source CGG frames, keeping source crop rectangles and layer ordering, horizontal/vertical flip, opacity and 90-degree rotation according to the independent 2016 [BFFrameAnimator reference](https://github.com/BluuArc/BFFrameAnimator/blob/master/src/Frame.java). Additive blend is deliberately **an approximation**, and frame timestamps are not used to imply native timing.
- The produced preview has 23 nonempty RGBA cells, each 480×400, arranged in five columns (atlas 2400×2000). Deterministic raw RGBA digest: `2c59d87d592f86a77abbf9330e324603047819d7040cf5c5d7ed0f6be250f322`. The source original thumbnail is copied without pixel modification.

## In-game display and strict boundaries

- Collapsed **7★ Water visual source preview** inside the read-only Unit Encyclopedia for original archived form `20016`; an explicit frame slider lets the user inspect source-composited frames with **no assumed frame-rate/timing**.
- This is a static developer/reference view. It does not unlock Water 7★, update ownership, change stats/level caps, activate Brave Bursts, alter the current DEMO renderer, or interpret type-2 evolution materials as payable items.
- It does not modify the current 72 playable forms, saved `P.unitExp`, `P.evolutions`, `P.roster`, `bf_global_offline_demo_v7`, or `P.version===7`. The Android app/package/signing are unchanged.
- The source PDF/asset archive is not required at runtime: the source PNG/CSV slice is embedded into the source repository as one build-time base64 ZIP. The generated atlas and original thumbnail are bundled into the APK after hash verification.

## Verification

- `prepare_original_seven_star_water_visual_v129.py` validates the exact six original source-file byte lengths and SHA256 hashes against v127 before composing any preview.
- `test_bf_original_7star_water_visual_v12900.py` verifies the source, 23 deterministic nonempty frames, strict non-playability metadata, offline Chromium canvas rendering, and unchanged existing v7 save state.
- `test_bf_packaged_7star_water_visual_v12900.py` verifies that the signed debug APK contains the exact source pixel atlas and read-only adapter.
- v129 feature-head CI must pass before merge; v128 main build must pass before promotion; fresh merged-main CI must pass before marking v129 verified.

## Next step toward actual playable 7★

Cross-validate native sprite transforms and original 7★ evolution type-2 material handling, plus original EXP Lv101–120 and player type bonuses. Only then implement a correctly gated player-owned 6★→7★ evolution with separate save compatibility tests. This proof-of-render does **not** shortcut those mechanics.

Owner remains installed at **v124**, with next preferred APK update approximately **v150**.
