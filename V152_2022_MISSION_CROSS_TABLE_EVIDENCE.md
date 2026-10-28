# v152 — Original 2022 Global mission reference cross-table evidence

## Finding from the owner's original SHA-verified archive

This is **research-only**, not a playable quest unlock or an enemy-wave decoder. The original owner-supplied 2022 `mst-decoded.zip`, SHA256 `69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9`, contains three independently labeled sources that reuse the same **opaque** field `MISSION_8f4NYKxb`:

- `F_MISSION_MST_1_Ver1118.json`: 106 verified live missions plus 36 Amdahl source-only missions.
- `F_GRAND_MISSION_SPOT_MST_Ver92.json`: grand-mission spot records.
- `F_RAID_POINT_MST_Ver57.json`: raid point records.

In the 142 source-verified quest set, **92** mission reference strings have exact matches in at least one Grand Mission Spot row, **99** have exact matches in at least one Raid Point row, and **73** match both sources. Counts reflect *matching 2022 ordinary mission records*, not a count of grand/raid quests or unique strings.

The existing original `F_DUNGEON_MST_Ver1002.json` battle-background filename matches the numeric suffix of the *first* opaque reference in **133/142** mission records. The **nine exceptions** are missions 70–73 (first reference 10400 while background is dungeon_battle_10700.jpg) and 230–234 (first reference 20401 while background is dungeon_battle_20400.jpg). All **36 Amdahl** source-only missions match, but no uniform mapping is claimed.

An exact reused string is evidence of cross-table consistency, **not proof of enemy IDs, wave schedules, encounter weights, enemy AI, combat formulas, or loot**. No semantic assignment is made to colon prefixes or reference values. Original source missionBattleCount is a wave **count** only.

## Reproducibility and protections

The original 142-row subset is stored in a deterministic compressed, source-pinned 2022 evidence fixture. Each row records: mission ID, exact opaque group string, archived dungeon background, number of Grand Mission Spot rows with the exact same string, and number of Raid Point rows with the same string. Canonical SHA256 of rows: `2acd1ab29b8a00b3c8804a89fdc9d7b99cba4853f5974f765bc7473c89e7a284`.

CI cross-checks all 142 rows against the current source manifests: 34 original Mistral, 36 Morgan, 36 St. Lamia, and 36 original Amdahl. It asserts the cross-context counts and nine exceptions. When the original 2022 `mst-decoded.zip` is provided via `BF_ORIGINAL_2022_MST_ZIP`, the same test also verifies SHA256 hashes of the four original tables and reconstructs all 142 exact records directly from the primary source. The original archive is not required to be redistributed in the public repository.

No Android asset, Java/Kotlin, live quest list, save format, battle engine, summon/evolution, enemy AI, unit roster, package ID, signing or permission is changed. **Exactly 106 quests remain playable; the 36 Amdahl missions remain research-only.** The current installed v124 APK is not modified.

## Next gameplay requirement

Acquire a trusted original 2022 standard-quest *per-run mission configuration* or an equivalent authenticated formation table resolving the opaque strings into ordered waves/enemies with AI and rewards. Cross-table reuse and shared background numbers are insufficient. Separate historical 2014 mission snapshots are not 2022 native-source proof.

Source-backed gameplay restoration should follow after the original enemy formations and native AI behavior are independently established. Gate on exact feature-head GitHub Actions and new merged-main CI.
