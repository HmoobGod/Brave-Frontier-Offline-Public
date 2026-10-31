# v221 — Original 2022 Legend Stone item thumbnail (read-only Exchange Hall reference)

**Status:** Draft pending independent Claude exact-head review and CI; no playable 7-star/8-star evolution, inventory migration, purchase, reward or player-save modification.

## Original 2022 source evidence

Owner-verified original 2022 Global mst-decoded.zip SHA-256: 69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9.
Original 3-mst-translated/F_ITEM_MST_Ver1027.json SHA-256: 0286402bad6071687a698665e4a12cafdf7aaf9bbc6c131816cd5c2235857474.
Its original item 110100 (神越の魂石, type 4, max stack 999) specifies thumbnail item_thum_111000.png.

Owner's original BF1_item_part001.zip (4,205,647 bytes) SHA-256: 735c50613f55a84d8a3717a4ee53ef513c694031aa44963c43e24b597f134e2c.
Inside it, content/item/item_thum_111000.png is a byte-original 98x98 PNG, size 6,370 bytes, SHA-256 c3decdc9ce4403cf12bf022b0ff233f802b11883105d125a6c0877d85135e0e7, Git blob SHA-1 ce0dc4d12c3ad5806e1cf6e41424484dbf3ba924.

The earlier v137/v153 work already established the historical Legend Stone source ID and Merit Exchange Hall reference. This revision **only displays its original icon** inside the existing v153 read-only panel.

## Code, tests, and safety

- The original PNG is committed to app/src/main/assets/content/item/item_thum_111000.png. No retouching, generated imagery, or transformed saved source assets. It is displayed at CSS 64x64.
- source_data/bf_global_2022_legend_stone_item_art_v221.json records exact source and image hashes, item identity, dimensions, and all-false gameplay/save/transaction claims.
- app/src/main/assets/bf15300_legend_stone_merit_source.js adds an accessible image and visual-reference caption, not a button, reward or spending flow.
- test_bf_original_legend_stone_item_art_source_v22100.py checks SHA-256, Git blob hash, PNG dimensions, original v137 source manifest metadata, byte identity and no-write flags. Owner-local optional archive checks use BF_ORIGINAL_2022_MST_ZIP and BF_ORIGINAL_2022_ITEM_PACK_ZIP environment variables; private archives are not committed.
- test_bf_original_legend_stone_item_art_browser_v22100.py verifies actual image load in Chromium from a local file fixture, v153 integration, idempotence, no JS errors and unchanged fake v7 save, P and S.
- test_bf_packaged_original_legend_stone_item_art_v22100.py compares PNG/JS to the assembled Android APK and verifies package/offline/v7 identity.
- The Android workflow includes these tests and a new exact-head source preflight runs the standard-library source verification on PRs and merged main.

**Hard boundary:** The icon is not proof of the native original 2022 inventory, Merit balance/earning/spending, item grants, EXP threshold curves, native BB/LS, 7-star/8-star visual transforms, or 7-star/8-star playable evolution. Existing quest, combat, AI, loot, Gems, Imps, save fields, user-installed APK, Java/Android source, signing, app permissions and v7 saved progress are not changed.

## Review and merge gates

Base is merged v220 main SHA 3eda7783e96c3f3cc41e605c0c2512a6366a4a08. Require v220 merged-main Android Build #1169 completed SUCCESS. Require independent Claude APPROVE on exact v221 PR head, exact-head original item source workflow and full Android CI SUCCESS (including browser and APK checks), unchanged base and head, SHA-guarded merge, and fresh merged-main source and Android success. No promotion to Current without owner device and save-compatibility acceptance.
