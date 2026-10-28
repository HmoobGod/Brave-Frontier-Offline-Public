# v137 — Original 2022 Global Legend Stone acquisition reference

The original 2022 Global game records now establish not only **what** the special 7★/8★ starter evolution catalyst is, but **where it was historically obtained**. This is source recovery, not live currency or item grants.

## Source evidence from the owner's original archive

Verified `mst-decoded.zip` SHA256: `69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9`.

- `F_ITEM_MST_Ver1027.json`: item ID **110100**, original Japanese name `神越の魂石`, item type 4, thumbnail `item_thum_111000.png`, stack limit 999.
- `F_UNIT_EVO_CATALYST_COMMENT_MST_Ver139.json`: the original catalyst entry explicitly states **Farmable Locations → Mission Exchange Hall**, for material type 2 and ID 110100.
- `F_ACHIEVEMENT_TRADE_MST_2_Ver432.json`: **59 named “Legend Stone” exchange offers** for this item ID (plus seven historical rows with *other* names but the same item ID, kept distinct and not reinterpreted). The archived source table spans recurring 2017–2022 entries.
- The last four **original 2022** named “Legend Stone” exchange offers are **Jan, Feb, Mar, Apr 2022** (exchange IDs `80000056–80000059`), each **one item** with original `exchangeHallCost=4000` and `exchangeHallLimit=99`, and monthly window endpoints ending May 1, 2022. **The source does not identify the currency from this table alone.** Do not subtract 4,000 Zel, Karma or event points without proving the denomination.
- `F_UNIT_EVO_MST_Ver597.json`: **279 original type-2 evolution links** reference ID 110100; twelve are the six starters' 6★→7★ and 7★→8★ steps, already independently source-authenticated by v127/v130. Those twelve preserve their own Zel/Karma costs and *other unit materials*.
- Original 2015–2017 `F_ACHIEVEMENT_TRADE_MST_1_Ver432.json` also contains 58 older entries, mostly named Legend Stone with historical cost 8,000. They are distinct time-limited historical exchanges, not simultaneous permanent offers.

## What is actually new

`source_data/bf_global_2022_legend_stone_exchange_v137.json` retains the exact source identities/hashes, 59 named historic exchange tuples, all 279 original typed evolutions requiring item 110100 and all 12 starter joins. Canonical compact tuple SHA256 `1eb4ede7ead65cb2e8816cf6ef8578c0b68d186aa43b65a89b97f20cccd9215a`.

`test_bf_legend_stone_acquisition_v13700.py` validates 2022 April acquisition window, original 1-item output and numeric/source limits, immutable IDs, source file hashes, original v130 typed material / Zel / Karma join, all 279 source use cases, and unchanged `bf_global_offline_demo_v7` save contract. The test explicitly **rejects treating historical expiry dates as an offline-playability gate**.

## Game restoration requirements before activation

1. Authenticate original Exchange Hall **cost currency**, how that currency is earned, and whether inventory stores item 110100 separately from unit materials.
2. Reconstruct a persistent offline acquisition path (historical rotating availability cannot simply expire on a 2026 offline installation) without inventing free rewards or silently changing the original cost.
3. Preserve 2022 authentic item-versus-unit requirements and the v7 save format with optional migration/recovery regression. Never spend a stored unit-material count in place of an item.
4. Only then enable the first 7★ playable evolution once original animation, BB/LS and level-120 progression gates pass. 8★/Omni levels require the v136 shard/item/duplicate requirements too.

This patch is deliberately **read-only source evidence**. No new playable forms, item purchase, inventory, exchange currency, player resources, EXP, damage, CGG animation or signed APK changes. The user remains installed on v124 until planned v150.

Branch `feature/v137-original-legend-stone-acquisition-source` is stacked on v136 exact head `a2b8d8254872e259737b2b50ba3d2df02ab1fee5`. Require v134, v135 and v136 exact CI + merged-main SUCCESS and v137 exact feature SUCCESS before merging v137; then fresh main CI SUCCESS.
