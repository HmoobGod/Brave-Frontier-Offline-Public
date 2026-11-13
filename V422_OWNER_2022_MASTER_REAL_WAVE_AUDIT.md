# v422 — Owner-authenticated original 2022 master: first real source-only wave-join scan

**Status:** read-only source research. This is NOT original 2022 ordered MissionStart formation authentication, enemy-ID decoding, battle-AI evidence, drop authentication, gameplay integration, or release approval. Original native ordered wave coverage remains **0/106**.

## Provenance / execution, 2026-11-13

- The privately retained owner's `mst-decoded.zip` was found in the existing Brave Frontier Drive archive and read locally, not committed, extracted onto a public repository, or uploaded elsewhere.
- Full ZIP size **61,471,567 bytes**; full SHA-256 **`69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9`**: exact match to the source gate pinned in v175/v176.
- `3-mst-translated/F_MISSION_MST_1_Ver1118.json` SHA-256 **`d4e364b6c1c5a825c0153c57bdd4123cd35800c74db795d913d119b6c9a99f83`**: exact match; 1,717 source rows.
- The repository's v152 compressed cross-table fixture was fetched separately, and both its compressed SHA **`cc8aeda4a3f95555985bf4aada5c75f1f1dfdb67f0ee800d36b7aba56327f59a`** and canonical 142-row SHA **`2acd1ab29b8a00b3c8804a89fdc9d7b99cba4853f5974f765bc7473c89e7a284`** matched. All **142** pinned mission IDs and raw `MISSION_8f4NYKxb` reference strings matched the real original mission master; those rows comprise **29 distinct opaque reference strings**.
- An **independent local, read-only implementation of the v175 top-level and v176 bounded nested exact-string matching algorithms** scanned all **146 other** `3-mst-translated/F_*.json` master tables (147 including primary mission master). This was not claimed as a literal execution of the two repository CLI programs. The same ZIP checksum, primary-master checksum, v152 checksums, whole-string equality, 80 MB table limit, depth 8 / 2,000,000 node bounds, and no-unzip rules were applied. **0 tables skipped** in either scan. Only aggregate table names, fields, counts and status flags appear here; no private raw source rows.

## Exact-string top-level candidates

| Original table | Exact field | Distinct matching pinned mission IDs | Matching table rows |
|---|---|---:|---:|
| `F_RAID_POINT_MST_Ver57.json` | `MISSION_8f4NYKxb` | 99 | 110 |
| `F_GRAND_MISSION_SPOT_MST_Ver92.json` | `MISSION_8f4NYKxb` | 92 | 72 |
| `F_MISSION_MST_2_Ver1118.json` | `MISSION_8f4NYKxb` | 67 | 66 |

The bounded nested scan found **zero additional exact-string candidate paths**. This is a complete result only within that scanner's explicitly limited match definition, not proof that no encoded formation/group join exists.

## Schema triage: avoid false native-formation claims

- `F_MISSION_MST_2_Ver1118.json` has **1,716 rows** and the same set of **36 mission scalar field names** observed in the original mission-master layout, including `missionBattleCount` and `MISSION_8f4NYKxb`. Mere duplicate opaque text is not a wave-order or enemy join.
- `F_RAID_BATTLE_GROUP_MST_Ver52.json` has **11,121 rows**, with keys `battleGroupId`, `raidRouteId`, `AI_CHANCE`, and `raidAiId`. This is a *raid* table and does not establish an original 2022 Grand Gaia campaign mission-to-enemy roster join; no unsupported raid-to-campaign transfer is authorized.
- A separate owner archive manifest, `2022APR03-FULL-GL.txt`, enumerates **71,664 URL lines** and includes `/mst/*.dat` file URLs. URLs are an inventory; without byte-provenanced decoding they do not provide original battle starts.
- Exact token reuse across mission, raid-point and grand-mission spot rows **is not** proof of source-to-encounter resolution, ordered waves, monster IDs, stats, AI or loot. The 2014 donor Mission #10 variants and 2026 synthetic/designed data remain distinct and **must never** be promoted as 2022 formations.

## Next gates (all remain blocked)

1. Independently rerun the repository's **actual** v175 and v176 CLIs on this SHA-verified ZIP and compare their aggregate output with the independent local results above.
2. Identify and byte-pin the original 2022 client decoder/mission-reference-to-encounter-group path, join keys, and explicit failure behavior; compare to a separately authenticated `/mst/*.dat` interpretation if legitimately available.
3. Demonstrate concrete **ordered wave enemy IDs and multiplicities** for at least one playable mission with source-proven mission ID, battlegroup joins, boss designation, and no ambiguity. Independently prove stats, AI and drops before calling those authentic.
4. Then prepare a separate opt-in/staged gameplay patch with fail-closed fallback, external exact-head Claude approval, complete Android CI, one-PR guarded merge, green merged-main CI and owner Android acceptance.

## Safety/visibility

**No raw ZIP, archived master JSON rows, original account information or decompiled source bytes are in this repository commit.** No player/APK code, Java, manifest, signing, app ID, INTERNET permission, runtime battle logic, save, item/capture, enemy/NPC AI, economy or assets changed. Working APK and canonical `bf_global_offline_demo_v7` untouched. This document is a research checkpoint only; **nativeFormationDecoded=false**, **nativeEnemyIdsDecoded=false**, **nativeAIDecoded=false**, **nativeDropsDecoded=false**, **gameplayMutation=false**, **saveMutation=false**.
