# v183 — 54 genuine archived BF1 unit thumbnails recovered (source only)

We recovered **54 original PNG thumbnail files**, without alteration, from the owner's archived `BF1_unit_part007.zip` in their Drive BF1 Asset Packs. The complete original archive checksum SHA256 is `ad937083a4d023228f8796d45e5edd6adaf575872270476be994121941db3556`, matching the manifest `BF1_asset_packs_manifest.json` from the owner's BF1 Grand Archive extraction. This archive contains 3,394 thumbnail-named images; our scoped selection contains exactly the **54 previously missing historical enemy IDs** identified by v181/v182.

**Source bank:** `source_assets/bf1/BF1_Global_Archived_54_Enemy_Thumbnails_v183.zip.b64` stores the exact `381,418`-byte ZIP (SHA256 `0030b4bac35055b4ca5c4791464f56e406a37e74d4c9539f46711da8289734fd`). It contains 54 unchanged original PNGs totaling **377,608 bytes** and `BF1_54_Archived_Portrait_Provenance_v183.json` with per-file SHA256, historical source appearances, ID and mission coverage. The original `content/unit/img/unit_ills_thum_<id>.png` paths are preserved.

## Important source boundary

These **are real archived Brave Frontier unit portrait thumbnails**, and their numerical unit IDs are present in the owner's SHA-pinned 2022 Global unit/form catalog. But the BF1 Grand Archive is a combined historical resource, so this result does **not independently establish that each of these exact pixels was served in the 2022 Global client**. Nor does it establish original 2022 **battlefield sprites**, native wave composition, enemy AI, damage, drop rates or stage positioning. The recovered images are not substituted for battlefield sprites and never used to infer source combat.

## Strictly isolated from Android until review

This PR adds only the archive source bank, source-only verifier, this documentation and CI invocation. It makes **no changes** to packaged Android assets, Java/JS, evolution, summon pool, enemy logic, inventory, quest clears, Gems/Imps, Energy, save `bf_global_offline_demo_v7`, signing or permissions. Existing curated 127 historical-2022 unit thumbnails remain untouched.

`python test_bf_archived_54_original_portraits_v18300.py` refuses modified packed ZIP bytes, missing/extra files, divergent original source archive SHA, unsupported unit IDs, missing metadata, modified PNG bytes, missing names and mislabeled 2022-native formation claims.

**Claude independent review required before activation:** Verify the original archive provenance and id/collision resolution, how thumbnails would be displayed in the read-only encyclopedia, source-era labels, Android integration boundaries, and actual on-device v124 save migration. Do not merge a future Android-activation patch until Claude approves and exact-head feature and post-merge CI pass. Data-only retention of these genuine images can be merged without behavior review after the previous merged-main gate and this exact-head CI.

**No images were AI-generated or fabricated.**
