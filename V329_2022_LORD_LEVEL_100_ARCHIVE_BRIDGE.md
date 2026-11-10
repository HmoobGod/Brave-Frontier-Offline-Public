# v329 — Original 2022 Lord level-100 combat endpoint (DEMO EXP bridge)

## Gameplay change

The archived 2022 original Global unit master verifies exact Lord max-level HP, ATK, DEF and REC for 72 original playable starter-related forms. 60 already reached their source Lord endpoints under the legacy offline DEMO level cap of 99. Twelve 6-star forms (#10015/#10025 and corresponding 20000–60000 element forms) have **source max level 100** and could previously never reach that endpoint in playable archive combat, regardless of accumulated saved DEMO EXP.

This change uses the **existing DEMO level-threshold scale**, not a reconstructed original 2022 leveling curve: the legacy level-99 threshold is 24,255 accumulated unit EXP; the next DEMO 99→100 step is 495 EXP, so level-100 requires **24,750 DEMO unit EXP**. The global `demoLevel()` routine still stops at 99, preserving player display, training and saved semantics. For a legitimate newly constructed **archive** actor at DEMO level 99 with >=24,750 saved unit EXP and exact source max level 100, the existing source Lord max endpoint adapter adjusts that actor in memory to **Lv.100 and the fully verified 2022 Lord max-level stats**, then the existing Imp and 2022 starter leader effects apply in their established order.

This enables all 72 source-exact Lord max endpoints without pretending original native EXP patterns 10/15/20, intermediate growth/rounding, native unit types, original enemy formations or combat damage are recovered. It is still labeled offline DEMO progression, not faithful 2022 leveling.

## Safety gates

- Verify source-qualified **exact unit ID, cap=100, original Lord max endpoint**, owned base unit, original squad slot and effective evolution mapping.
- Verify a fresh constructor unit at level 99 from the unmodified demo progression, and exact unmodified DEMO HP/ATK/DEF/REC baseline before applying source stats.
- Require >=24,750 valid DEMO EXP. At 24,749 EXP leave level 99 and preexisting DEMO stats intact. Cap <100 forms are never promoted to level 100. Reapplying to the same actor does not stack.
- Reject training, unknown or unowned forms, altered builders, invalid levels and missing source records. No writes to `P`, `P.unitExp`, `P.squad`, roster, progression, `bf_global_offline_demo_v7`, original or custom rewards, Android package ID or signing.
- New level-100 actor endpoint is **battle-only**. The existing demo EXP display may still show level 99 outside the current battle; the source-based battle level is correctly labeled as a DEMO adapter.

## Acceptance

The v172 Chromium regression now exercises all 72 evolved source forms and confirms **72/72** exact max Lord stats with 12 source-level-100 forms bridged, proper starter leader stacking, threshold 24749 versus 24750, normal 4/5-star cap preservation, training isolation and save invariance. Packaged APK checks the source threshold code, original Lord module load order and unchanged Android signing. Full exact-head signed Android/Chromium CI required before merging; do not release without owner in-place upgrade test. If parent main moves, reconcile byte-exact changes onto the new main and require fresh combined-tree CI.

Reference primary owner archive: `mst-decoded.zip` SHA256 `69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9`. Existing `bf_global_2022_playable_lord_stat_endpoints_v116.json` and `BFGlobalOriginalLordStatsV11600.endpoint()` validate the exact source values.
