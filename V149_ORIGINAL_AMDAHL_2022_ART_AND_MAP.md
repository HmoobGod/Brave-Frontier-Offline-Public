# v149 — Original 2022 Brave Frontier Global Amdahl art + offline map preview

This is a genuine asset-restoration step toward the next original playable region. It **does not falsely unlock incomplete quests** or replace verified 2022 enemies with synthetic ones.

## Original 2022 archive provenance

The owner's authenticated original BF1 Global Google Drive source pack ZIP files were fetched in full, overcoming a Google Drive 100-item folder listing truncation. SHA256 checks verified the original archives exactly:

- `BF1_area_part001.zip`: `17b7da1c4dc3e82a454571f5b4983e54ef95d1eff7eb19a808f1ea39ced98082`
- `BF1_dungeon_part001.zip`: `a748f675fd8271c0f41bb0b9244c83ffc5d23b4051cfd757494d16735c506644`

Nine original source assets are copied without modification into a deterministic, source-hashed **694,583-byte** slice `BF1_Global_2022_Amdahl_Original_Art_v149.zip`, SHA256 `65790b0c0e9099fedb347e4a0c53f76bde7ebe3ea0cb7b9089557cf51c759179`:

- 640×960 original 2022 `content/area/area_0004.jpg` world-map image and `area_plate_0004.png` plaque.
- Seven source-original 2022 battle background JPEG files `dungeon_battle_50100.jpg` through `dungeon_battle_50700.jpg`, independently matched to the original Amdahl dungeon master IDs 400–460.

Source metadata pins each original byte count and SHA256; the original dungeon map coordinates were decoded from authenticated 2022 `F_DUNGEON_MST_Ver1002.json` rows (`QUEST_SnNtTh51` = source x, `QUEST_M6C1aXfR` = source y), and checked with the original 640×960 pixel geometry. All seven source dungeon names/IDs/backgrounds/prerequisites match the exact v147 original 36-quest source manifest.

## Visible but read-only milestone

The existing Grand Gaia campaign has 106 playable source-identical 2022 Global quests through St. Lamia. The new separate, collapsed **Amdahl Original 2022 Map & Dungeons (Preview)** in the Quest screen shows the genuine Amdahl world map, source-based clickable location pins and original JPEG battle scenes for all seven dungeons. The reference explicitly warns that 2022 native enemy formations/AI remain undecoded and quests 400–465 are **not playable**. It does not hijack the three existing Grand Gaia region tabs, alter quest selection, simulate costs, unlock any quest, or grant rewards.

The feature script is optional and fail-closed if exact known v7 save and 106-quest baseline is unavailable. It never calls save or localStorage writes. Independent Chromium checks source pins, rendered original images and no player/live-state or save changes. Android signed APK checks nine exact original image hashes. Source JavaScript remains under the 64-KiB WebView asset limit.

**Safety:** `P.version===7`, `bf_global_offline_demo_v7`, Android signing/package, all existing units/saves/quests/BB, main-story battle behavior and current v124 installed user experience remain unchanged. Read-only provenance does not assert native 2022 mission encounter recovery.

## Required verification and future work

This branch is stacked on v147 Amdahl **source manifest** (`41f984f736dd4830c8bcde3c2cb8e297dd31abf2`) and earlier v146. Require sequential exact feature-head CI SUCCESS + fresh merged-main SUCCESS for v143-v147 before merging this stage; then verify v149 exact feature and fresh merged main. Actual original Amdahl playable mission unlock requires original 2022 native wave/enemy/loot source and safe expansion of existing 106-quest UI/save assumptions; don't invent those.

The owner is still on installed **v124** and prefers the next APK update at **v150**.
