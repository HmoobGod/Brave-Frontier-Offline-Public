# v224 — Original 2022 Global evolution-material reward and exchange source evidence

**Source-only; no gameplay or app change.** This version analyzes mission-reward definitions and historical exchange-hall source references for the original 31 evolution *item* material IDs recorded in v222. It does **not** issue rewards, add inventory, activate Merit purchases, enable 7★/8★ evolution, change combat, or touch the canonical v7 save.

## Provenance and scope

The owner-original `mst-decoded.zip` (SHA-256 `69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9`) contains translated mission tables `F_MISSION_MST_1/2_Ver1118` (3,433 combined rows) and achievement trade tables `F_ACHIEVEMENT_TRADE_MST_1/2/3/4_Ver432` (32,500 combined rows). v224 records exact SHA-256 pins for each of those six source files and matches only `type=4` rewards/offer items to the **31 original item-master IDs** from the v222 catalog; type-1 *unit* evolution materials are never accepted as items.

- **Mission reward source references:** exactly 10 matching `4:itemId:...` tokens across **9 missions**. These are archived mission reward *definitions*, not authenticated repeatable drops, claim execution or ownership. One mission has two material item references. The original reward strings and mission names are preserved (including Japanese text).
- **Historical exchange source references:** exactly 152 matching records across 15 distinct material item IDs, including 124 references to Legend Stone 110100. Archive fields include cost, limit, start/end dates and legacy source shapes. **36 of the 152 entries have four colon-separated fields rather than five**, all of them Legend Stone: v224 accepts both shapes but does not infer semantics for the missing field. One original start date reads `1016-10-27`, demonstrating why we cannot simply activate historical calendar rules from archived strings.
- Earlier v153 had separately source-pinned April 2022 Legend Stone listings at 4,000 Merit. v224's translated archived exchange tables contain historical entries from older periods with other prices, often 8,000; these sources have different scopes. **Do not merge price claims into one active live economy** or override the v153 reference based on v224.

## Fail-closed test contract

`test_bf_original_material_acquisition_source_v22400.py` verifies all six source table paths and hashes, unique mission IDs and exchange offer IDs, 31-item type boundary, 10/9 and 152/15 counts, canonical row and offer SHA-256 digests, both historical token shapes, and all-false gameplay/inventory/save/purchase flags. With `BF_ORIGINAL_2022_MST_ZIP` supplied, it independently re-derives mission rows and all 152 exchange references from the pinned owner archive and checks each table's SHA-256. Public CI is source-only and **does not** independently open the owner's original archive; a green run proves internal committed integrity, not original ownership or complete live acquisition semantics.

Before any playable reward integration, independently authenticate per-mission accessibility, reward eligibility, initial vs repeat clears, probability if relevant, claim idempotency, counter/limit rules, item stacking, error recovery, save-version migration, and compatibility with existing user saves. No owner Current APK promotion.
