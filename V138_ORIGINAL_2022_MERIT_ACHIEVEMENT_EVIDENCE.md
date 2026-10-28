# v138 — original 2022 Global non-expiring Merit Point achievement evidence

The owner's **original** 2022 Global `mst-decoded.zip` (SHA256 `69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9`) includes 3 distinct `F_ACHIEVEMENT_SUBJECT_MST_1/2/3_Ver503.json` translated files, with **15,173 original achievement rows and 15,173 unique source IDs**. This revision source-pins **657 records** that explicitly have a positive numeric `meritPointReward` and original `availabilityTimeEnd="9999-12-31 23:59:59"`.

The 657 immutable source records retain original record part, `achievementSubjectId`, literal English name and description, original `achievmentType` numeric code, raw requirement parameter `ACHIEVEMENT_t5R47iwj`, original Merit reward, and the sentinel expiry. The 85,666-byte canonical JSON is compressed losslessly to **12,068 bytes** and committed as a source-only JSON metadata file. Its source-record SHA256 is **`bf708759dc3d57ade12980bf72569e407889f476817938790b85259d2cc9ca22`**, independently checked by `test_bf_global_merit_achievements_v13800.py`. Raw source file digests are also pinned in the metadata.

## Source-supported candidate achievement groups

| Original `achievmentType` | Source record count | Example original requirement | Source Merit Points |
|---|---:|---|---:|
| `100` | 12 | 10 Daily Log Ins | 100 |
| `700` | 12 | Player Level 10 Reached | 100 |
| `8500` | 14 | 10 Overall Quests Cleared | 100 |
| `5400` | 16 | 10 Sparks Produced | 100 |
| `8600` | 63 | “Creator of the World” Cleared | 100 |
| `12640` | 42 | Fire Element Level 5 Reached | 500 |

These are **original source labels and values**, not proof that our current DEMO counters implement the native achievement event or that every original record is individually claimable today. Other original source records ending in 2022 are *not* imported into the non-expiring subset. The sentinel end date describes the source's recorded availability only: it does NOT prove repeatability, no time-based daily reset, or native reward conditions. The source has multiple condition fields, including overloaded `availabilityTimeStart` that may hold counter parameters rather than a date.

## Why this matters to playable evolution

The original 2022 `F_ITEM` and Evolution/Mission Exchange data already pin the Legend Stone (type-2 item ID **110100**), its historical **4,000 Merit Points** Exchange Hall cost (independent archived historical wiki corroboration for the currency) and the 279 original type-2 evolution links requiring it, including all twelve starter 6★→7★ and 7★→8★ recipe steps. This revision provides source-authentic *potential* ways for the future offline player to earn that currency without inventing grant amounts.

**No grants / purchases / save edits:** This revision must remain source-only. It does not alter `P.version===7`, `bf_global_offline_demo_v7`, roster, quest completion counters, Merit balance, inventory, rewards, battle AI or original unit skills. Before live implementation, independently map specific `achievmentType` codes and original award ledger to our existing logged events, add transaction idempotency and rollback/recovery tests, and preserve save compatibility. Old April 2022 Exchange Hall windows must not automatically expire in 2026 offline use; nor should original 2022 limited-time event achievements silently become permanent.

CI/test gates: v134, v135, v136 and v137 feature and merged-main CI success before promotion; v138 feature-head CI and main CI success. Owner installed v124; planned next APK v150.
