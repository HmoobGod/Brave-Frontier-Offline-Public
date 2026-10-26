# Brave Frontier Global v50.00 — Original Party ATK +50% Item

Start from exact green v49 build, preserving all original gameplay source tables, archives, Android package identity and v7 saves.

Source: `mst-decoded.zip` SHA-256 `69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9`; 2022 translated item table `3-mst-translated/F_ITEM_MST_Ver1027.json` SHA-256 `0286402bad6071687a698665e4a12cafdf7aaf9bbc6c131816cd5c2235857474`.

Original item **#50400 (総攻薬)** battle effect group 400, itemTargetArea=2 (all allies), passiveSkillInfo=`0,50,0,0,0,3`. The Japanese description explicitly says ATK +50% to all allies for 3 turns. v50 adds a source-indexed optional battle action that places a +50% in-memory ATK buff on all living allies currently below that boost, reusing the already implemented `currentAtkBoost()` combat path. Stronger active boosts are not overwritten. KO or empty slots cannot benefit. The actor takes a DEMO Guard action protected by v45's shared per-unit item-turn reservation and v48 Auto safeguard.

Original source-backed: item identity, percentage, duration, and ally-wide scope. **DEMO-only**: one temporary charge per battle, actor Guard cost, expiration counting cast turn as 1, stronger-only stacking rule, no real inventory, existing damage formula and animation effects. No persisted inventory or quest progress is edited.

Evidence-only records additionally identify original #50401 as single-target +100% ATK and #20401 as single-target +50% ATK; these are not enabled in v50.

Release gates: all inherited browser/APK tests; full-ally scope, KO and stronger buff protection, +50% in native demo combat path, turn expiration, shared item reservation, save isolation, and unchanged offline signing. Promote only exact successful CI commit.

## Source data expansion

In addition to item #50400's active effect, the app now bundles a **read-only compressed index of 99 original 2022 battle-item effect rows**, including legacy placeholder entries, from the same 1,668-row translated item master. The repository stores identical gzipped source and Android-asset inputs named `bf_global_2022_battle_item_effect_catalog_v5000.json.gz` (SHA-256 `c257f029c210cd402388fbe3fafb003da9f2e708a0beedfd89c09a811ebb7388`). Android AAPT expands `.gz` assets and removes the suffix, so the APK contains `assets/bf_global_2022_battle_item_effect_catalog_v5000.json` as decompressed JSON; tests compare its exact bytes to `gzip.decompress(source)`. Its schema identifier is `bf-2022-battle-item-effects-v5100` (dataset's extraction format; included starting release v50), with fields in order: itemId, battleEffectGroupId, targetType, itemTargetArea, skillTypeId, passiveSkillInfo, itemMaxEquipped. Item text and unused fields remain recoverable from the unchanged source archive; this index is not a substitute for full master assets. No new item behavior is automatically enabled by the catalog. The dedicated package regression verifies 99 rows and byte-accurate source/APK *content* identity after Android AAPT's standard gzip transform.
