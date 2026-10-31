# v222 — Original 2022 Global typed evolution material item artwork catalog

**Status: SOURCE-ONLY DRAFT.** There is no new APK artwork, original item inventory, item purchase, source gameplay, 7★/8★ evolution unlock, save migration, or user Current change.

## Original provenance
Owner `mst-decoded.zip` SHA-256 `69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9`, translated F_ITEM_MST_Ver1027 SHA-256 `0286402bad6071687a698665e4a12cafdf7aaf9bbc6c131816cd5c2235857474`, translated F_UNIT_EVO_MST_Ver597 SHA-256 `fbaae982125b78e5a203095d0bb6d8892d210c4a632aa9e2e24f70ba0e480deb`, and BF1_item_part001.zip SHA-256 `735c50613f55a84d8a3717a4ee53ef513c694031aa44963c43e24b597f134e2c` independently verified against owner archives.

## Verified coverage
All 1,342 archived evolution transitions were read. Exactly 7,107 slots of **type 1** refer to 85 distinct *unit-material IDs*, **not item-master IDs**. Exactly 333 slots of **type 2** refer to 31 distinct *item-material IDs*. The 31 names are preserved exactly as archived, including unresolved original `MST_EVOITEM_*` string keys and Japanese labels; we did not invent translations. Every thumbnail filename, file size and SHA-256 is from byte-original owner BF1 item assets. The canonical 31-row digest is `3c96e0a37f8fb9cf11b924f6ebb487edd2034f02c7c11f27d9991c6efd13065c`.

Legend Stone item #110100 occupies 279 slots and its exact PNG is already in the v221 source display. The other 30 original image files are **NOT** added to the APK by v222; their identities are staged for a separately gated future cosmetic-only feature. Do not confuse a verified asset with source-proven item acquisition, ownership or an unlockable evolution.

## Checks and merge gates
`test_bf_original_2022_evolution_item_art_v22200.py` verifies the committed catalog, counts, canonical checksum, strict filename paths and all no-gameplay flags. If the original owner archives are explicitly supplied via `BF_ORIGINAL_2022_MST_ZIP` and `BF_ORIGINAL_2022_ITEM_PACK_ZIP`, it reconstructs all 31 records from the real F_ITEM and F_UNIT_EVO tables and checks all 31 PNG byte lengths and hashes. The public CI suite does not include owner-original archives; do not claim that CI alone independently verifies original provenance.

Require independent Claude exact-head review, a green exact-head source workflow, unchanged base/head and SHA-guarded merge, then merged-main source workflow. Owner APK and saves are untouched.

Related source audit: https://drive.google.com/file/d/1JmNK0ZWmixfcaD9RTV7IznUiLO1Egq0C/view
