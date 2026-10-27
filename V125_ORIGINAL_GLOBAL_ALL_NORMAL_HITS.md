# v125 — All original 2022 Global normal hit frame references (read-only)

## Original-source recovery

The owner's original `mst-decoded.zip` SHA256 `69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9` contains 2,291 `F_UNIT_MST_1/2_Ver1084.json` entries. Parse four-number `damageFrames` tuples `frameTick:weight:kind:flag`, removing only whitespace from original IDs `20926, 51136, 820317, 850347`. Exclude source summoner #1 and original records whose hit damage percentages do not total exactly 100. Result: **2,258 valid original normal attack frame references; 33 excluded**. **Do not normalize** the 32 original non-summoner invalid entries.

Source-authenticated sorted `[unitId,[[frameTick,weight,kind,flag],...]]` canonical SHA256:
`e99e843c6d0c3c46b30fab217fb3c7415275ebf58782008a3a0127e90df0b836`.

The recovered records are encoded as unsigned base-128 unit-ID deltas, one-byte hit counts and big-endian 3-byte original four-field events; the 60,443-byte binary is gzip-compressed to 41,025 bytes and embedded as a 54,700-character base64 string in `bf12500_full_original_normal_hits.js` (total asset below the 64-KiB Java asset reader cap). The archive is decoded entirely offline with modern Android WebView/Chromium `DecompressionStream('gzip')`. Unsupported WebViews fail closed and leave existing gameplay functional; no network or mutable saved fields.

## What changed

- `BFGlobalOriginalNormalHitArchiveV12500.lookup(unitId)` exposes all four original source fields per valid archived unit after asynchronous decoding.
- The original Unit Encyclopedia displays those source frame ticks and weight percentages on demand. **This is read-only reference evidence**, not a way to recruit the archived 2,291 units.
- Original live normal attacks, including the 71 existing verified playable profiles, are unchanged. The source lookup does not modify `BF_ARCHIVE_NORMAL_HITS`, player battle or enemy AI, animation timing, damage, crystal pickups, quest loot, combat RNG, EXP, unit type, save keys or v7 state.
- `test_bf_original_full_normal_hit_archive_v12500.py` validates the exact binary digests, source count, all 2,258 hit-count joins against existing v84 evidence, all 71 playable source tuple matches, 33 exclusions, Chromium lookup/UI and no save writes.

## Important mechanics boundary

The four recovered `damageFrames` fields represent original source frame references. **60 frames/ticks per second has not been authenticated for the 2022 Global native client**; do not assert those frame ticks equal exact real-world playback seconds. Full original damage, sparking, multihit animation timing and 2022 native battle sequencing still require independent decomp/version-specific confirmation.

Preserve Android package `org.bravefrontier.offline`, persistent debug signing, `P.version===7`, `bf_global_offline_demo_v7` and all existing progress. Merge only after exact feature-head CI SUCCESS, then fresh merged-main CI SUCCESS.
