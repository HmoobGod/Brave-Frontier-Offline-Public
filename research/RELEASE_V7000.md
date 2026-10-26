# Brave Frontier Global v70.00 — Original Blessing Light #20100 Healing Potency

Base: v69 elemental-combat candidate, which retains v68's verified exact original Lv1–Lv10 healing BB data. This change must not be promoted unless the parent and the exact v70 commit pass all CI.

The recovered 2022 original item master `3-mst-translated/F_ITEM_MST_Ver1027.json` (SHA-256 `0286402bad6071687a698665e4a12cafdf7aaf9bbc6c131816cd5c2235857474`) explicitly records Blessing Light #20100 as `battleEffectGroupId=520`, `skillTypeId=2`, all allies (`itemTargetArea=2`), and healing payload **`500,500,0,0`**. Old v43 applied arbitrary **250 DEMO HP** because numeric evidence had not been incorporated.

This release uses the source-recorded **500 base HP**, capped by current missing HP for each living ally. KO allies still do not revive. Existing shared Guard actor reservation and one temporary DEMO charge remain unchanged. The effect is *closer* to original numerical balance but native item use timing, inventory, REC influence, and rounding remain unverified (clearly labeled). No new experimental item is added.

Original archived row, hashes and unknowns are stored in `source_data/bf_global_2022_blessing_light_v7000.json`. The inherited v43 Chromium test now asserts both capped 400 HP and full 500 HP recovery, no KO revival, no double item/Guard, stable mode/reset and v7 local saves. New regression and signed APK tests confirm source payload. Source master file, Android signer, application ID, manifest INTERNET omission and save schema are unchanged.
