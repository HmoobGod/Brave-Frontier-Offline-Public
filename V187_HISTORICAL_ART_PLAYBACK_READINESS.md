# v187 — CGG/CGS original BF1 source art: static playback-readiness validation

The v184/v185 recovery bank contains **374 byte-verified original archived BF1 art files** covering 67 historical enemy unit IDs. This patch inspects them as **source data**, not as an Android animation implementation.

## Structural findings from real art files

- **67 animation atlas PNGs**, 67 battle illustration PNGs, and **240 original CSVs** (67 CGG plus 173 CGS).
- The CGG files contain **1,111 raw rows**; CGS files contain **1,371 four-column rows**.
- Each CGS row's first integer is within the zero-based row range of that unit's own CGG file. This is **structural evidence of a likely row index**, not proof of playback semantics.
- Seven atlas PNGs have unusual, non-power-of-two width or height values. A future sprite renderer must respect actual source image dimensions and must not infer square 256/512 sizing.
- There is **one exact source CGS row with fourth integer zero**, `content/unit/cgs/unit_atk_cgs_10103.csv`, line 11, `18,-10,0,0`. This must never be treated as a nonzero elapsed time without independent specification. It may be a sentinel, transition or another field meaning.
- All battle illustration files have 108×108 pixel dimensions; these images are **not interchangeable with animation atlases**.

## Authenticity limits and next review

The combined BF1 archives are historically authentic source bytes, **not proven exactly 2022 Global client revisions**. Neither the CGS four-field meaning nor CGG transform groups, sprite layering, frame duration units, transparency/blending, flips, cropping, status overlays or native opponent assignments are independently established. No animation is activated and no 2014 formations, AI, hit/damage/drops are copied into the 2022 playable story.

`python audit_bf_historical_art_layout_v18700.py` validates byte-level source archive checksums and generates a **separate source-audit JSON artifact**. `python test_bf_historical_art_layout_v18700.py` enforces fixed empirical counts and the zero-row exception.

**CLAUDE REVIEW REQUIRED before Android art activation:** Verify all assumptions in the proposed read-only gallery first; for playable animation, require independent decode of CGG/CGS including the zero-duration source row and nonstandard dimensions. Enforce a strict disabled-by-default runtime gate, no localStorage/player `P`/`S`/`QUEST` mutation, no changes to `bf_global_offline_demo_v7`, and actual owner-v124 Android save migration checks.

Only source scanner, regression, docs, and CI artifact upload change; no Android/Java/JS asset, package/signing, network permission, quest, save, Gems/Imps or gameplay code changes. Original 2022 encounter formations remain unverified despite the real-v186 scan.
