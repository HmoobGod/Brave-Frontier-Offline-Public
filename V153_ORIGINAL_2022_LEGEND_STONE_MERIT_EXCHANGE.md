# v153 — Original 2022 Global Legend Stone Merit Points Exchange Hall source

## Why this matters for native 7★ progression

The owner's SHA256-verified 2022 Global archive contains the 2022 Legend Stone **source-only** Exchange Hall price: exactly **4,000** points for original typed evolution item **110100** (Legend Stone), with a historical offer limit of **99** for each monthly listing. Original item payload is `4:110100:1:0` and source table `F_ACHIEVEMENT_TRADE_MST_2_Ver432.json` is SHA256 `00fc854cdcf3f507ac0544a6e6774af5afad22cf89e0c1b535d11258ab3b54e9`, archived in original `mst-decoded.zip` SHA256 `69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9`.

Four original offers, IDs **80000056–80000059**, run January, February, March and April 2022, ending 2022-05-01 07:59:59 in the original source. The current installed reconstruction must NOT use those historical calendar dates as an offline availability gate. Prior v137 separately verified 59 original named offers (2015–2022), 279 original typed evolution recipes requiring 110100 and all twelve 7★/8★ starter recipes.

**Currency evidence:** The original archived table column is `exchangeHallCost`, which gives the original numeric value but does **not** explicitly label the currency. Independent historical Brave Frontier Global guides identify the Exchange Hall currency as **Merit Points**, and describe Legend Stone for 4,000 Merit Points on a monthly cooldown:
- https://bravefrontierglobal.fandom.com/wiki/Achievement_System (Exchange Hall, Other)
- https://redalert.cullison.org/r/bravefrontier/wiki/welcome (Missions / Merit Points and Exchange Hall)
- https://gamefaqs.gamespot.com/boards/757425-brave-frontier/74232004 (historical 8,000 Merit Points Legend Stone pricing in an older time window)

This distinguishes the source-exact **2022** numeric 4,000 cost from earlier **2015–2017** archived 8,000 cost. Do not represent the source column itself as a verified currency type. Independent player documentation is corroboration, not archived game code.

## Implementation / safety

Add a single additive, collapsible **read-only reference panel** after the v130 original typed evolution recipe inspector:
- Item ID 110100, source price 4,000 Merit Points, four historical 2022 monthly offers and source historical limit 99.
- Explicit statements that source periods do not limit present offline access, Merit Point earning/account balance/spending, item acquisition and evolution inventory are NOT enabled, and 7★/8★ forms remain source-only.
- Requires original source v130 read-only API and v7 player state, with no effects on `P`, `S`, `localStorage`, quest clears, roster or combat.

Tests cross-check embedded four 2022 records against existing v137 SHA-pinned manifest, twelve original typed evolution recipes, Playwright UI/idempotence and zero save writes. Optional offline original-archive regeneration with `BF_ORIGINAL_2022_MST_ZIP=/path/mst-decoded.zip`. Signed-APK packaging verifies byte-identical JavaScript and unchanged application/signing/offline identity.

This resolves original 2022 **item cost and historical currency context**, not the still missing **legitimate Merit Point earning, current inventory, full evolution material sources, native EXP/stat growth, 7★ renderer and native BB/SBB behavior**. Do not unlock evolution until those are proven and migrated safely. Owner's v124 installation remains untouched.

Merge gating: exact feature-head GitHub Actions SUCCESS, fresh merged-main CI SUCCESS before declaring v153 verified.
