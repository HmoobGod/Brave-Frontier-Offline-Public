# Brave Frontier Global Offline — v0.39.0 demo: Evolution Roadmap

Built directly from v0.38 (Build #68 branch at commit 81ef0408b97a1097b887e51da33d9314248ada0d). Offline player-facing Evolution Roadmap is available as a collapsible guide within **Units → Evolution Lab**.

## v0.39 — next-evolution materials and costs at a glance

- Pick any **owned** base unit to see its next currently playable original Global evolution form. The list follows the true base-ID ownership model across all **72 playable forms / 54 existing evolution recipes**; no inaccessible forms are invented.
- See **current material inventory / exact original source-ID requirement**, missing quantity for each catalyst, **original Global Zel reference** versus **actual demo Zel price**, and next evolution name. Finished lines indicate no next implemented form.
- The guide is opt-in and read-only. It does not grant materials, affect DEMO quest drops, mutate combat, save or import/export values, change the app ID or signing certificate, or change the **bf_global_offline_demo_v7** schema. For real evolution use the existing Evolution Lab button and its demo Lv.2 requirement.
- Catalyst milestone guidance is explicitly DEMO, not an assertion of original enemy loot tables. Unit names and recipes are read directly from existing source-verified v0.38 arrays, not an independently simulated progression.
- Idempotent build-time insertion, direct Gradle preparation, Chromium save isolation / source-rule tests, and APK packaged-HTML checks run after all existing v0.38 checks.

# Brave Frontier Global Offline — v0.38.0 demo: Original Global Alternate 6-Star Evolutions

Based on verified v0.37 Build #67, commit 472d302e371f433d1f4a37be1afb787d480ad15a. Active branch: feature/original-global-other-six-star-build68. Preserve the original 2022 archives, Android signing identity, and existing saved v7 progress.

## v0.38 — six other original Global 6★ evolutions, 72 playable forms

**18 recruitable base IDs, 54 evolved forms and 72 playable forms total.** Six original 2022 Global records from the existing Zegar/Zephu/Lario/Weiss/Luna/Mifune 5★ lines are newly playable, without adding summons or changing owned base IDs.

| Previous 5★ form | New original 6★ form | Original Brave Burst behavior |
|---|---|---|
| Beast King Zegar #10024 | **Inferno Beast Zegar #10025** | Imperial Ardor Claws — single enemy, source Injury effect unmodeled |
| Dragon Hero Zephu #20024 | **Tidal Dragoon Zephu #20025** | Raging Hail — single enemy, source Weak effect unmodeled |
| Bow God Lario #30024 | **Gaia Bow Lario #30025** | Meteoric Gust — all enemies |
| General Weiss #40024 | **Gilded General Weiss #40025** | Thunder General's Command — all-party ATK support, archived Lv1 second parameter **94** |
| Holy Empress Luna #50024 | **Radiant Goddess Luna #50025** | Live with no regrets! — all enemies |
| Ryujin Mifune #60024 | **Shadow Ronin Mifune #60025** | Secret Art: Shining Darkness — all enemies |

Authentic source-derived **6★ Lv.100 caps, unit costs, base and Lord HP/ATK/DEF/REC**, original English names, CGG/CGS battle sprite sheets, original thumbnails, source BB scope and 10 raw BB level records are retained. All original previous 66 playable forms and their art/skills remain intact.

**Do not infer native BB damage from unrecovered effect codes.** Five offensive BB records use original effect codes **1800, 2300, 3300, 3400** with parameters whose native meaning is not decoded. Combat retains the explicitly **DEMO 2.1×** multiplier for those skills, with verified single/all-enemy targeting. The source Lv1 support record for Gilded General Weiss is **0,94,0,0,0,3,170** (effect code 2500). The existing demonstration support model interprets that as **+94% ATK for three demo turns**. Original buff stacking, precise turn logic, status effects and attack formulas still need work.

**Evolution and catalyst accessibility.** Each original 5★→6★ recipe requires **500,000 original Zel**, plus the archived material IDs. All six include the shared catalyst **50354 ×1**, the applicable element's two upper-tier catalyst IDs, and shared **60144 ×1** and **60224 ×1**. The Evolution Lab charges **10,000 separately marked DEMO Zel** per fourth step; the original source Zel and actual materials are displayed. To avoid fabricating enemy drops, two new strictly DEMO quest milestones grant 60144 (every **30th** quest clear) and 60224 (every **36th** quest clear), in addition to existing 6th/12th/18th/24th material schedules. Demo Lv.2 before evolution is unchanged. Existing recipes, inventory and quest progress are preserved.

**Original sprite accuracy limitation.** The supplied 2022 PNG sheets are often **rectangular** (up to 1100 px tall). Source frames are reconstructed in 480×400 atlas cells with actual recorded scales and source-layer order; out-of-frame layers are clipped rather than discarded. Nonzero CGG orientation flags or reserved flags are **not** claimed as native-exact rendering. Luna has one layer with an additional raw transform value **90**, retained in the source manifest but not guessed as a specific rotation. Missing movement CGS for Lario and Weiss use the source idle sequence as a documented fallback.

**Save/security:** Still package `org.bravefrontier.offline` with save key `bf_global_offline_demo_v7`. All four original evolution stages for these six alternate lines update the same `P.evolutions[ownedBaseId]` mapping. Older v7 saves remain loadable; forged/unknown evolved forms are rejected. No network, microtransactions, new account requirement or overwrite of user backup assets.

**Evidence:** `source_data/bf_global_other_six_star_v038.json` and `source_assets/bf1/BF1_Global_2022_Other_Six_Star.zip.b64` embed exact source data and hash-verified original PNG/CGG/CGS assets. `prepare_original_other_six_star.py` independently checks 2022 Global catalog/English lore and builds sprite atlases. Browser regression tests verify the 72 playable forms, all six evolutions, real image loads, single/AoE/support BB scopes, source-only uncertain damage handling, catalyst schedules, v7 save recovery and invalid-ID rejection. CI checks all six final packaged atlases and portraits in the Android APK. This still is a partially restored **offline demo**, not a complete original game.

## v0.37 — playable original Global 6★ starter lines (66 forms)

Six complete original Brave Frontier Global starter evolutions are added from the archived 2022 master data and source sprite files, raising this **offline single-player reconstruction** to **18 recruitable base IDs + 48 evolved forms = 66 playable forms**. There are no additional base summons; each evolved form belongs to the previously owned base ID.

| Previous playable 5★ | New original 6★ | Archived Brave Burst |
|---|---|---|
| Fire God Vargas #10014 | **Holy Flame Vargas #10015** | Final Burst — all enemies |
| Ice Goddess Selena #20014 | **Holy Ice Selena #20015** | Last Blizzard — all enemies |
| Nature God Lance #30014 | **Holy Earth Lance #30015** | Eternal Symphony — all enemies |
| Thunder God Eze #40014 | **Holy Thunder Eze #40015** | Thunder Crush — all enemies |
| God Atro #50014 | **Holy Light Atro #50015** | Heaven's Gate — all enemies |
| Death Magress #60014 | **Unholy Magress #60015** | Bloody Chaos — all enemies |

Each has the source-backed **6★ rarity, original Lv.100 cap, unit cost, HP/ATK/DEF/REC base and Lord endpoints**, original English name, unit portrait, complete original CGG/CGS movement/idle/attack sequence and all-enemy BB target type. All ten recovered BB-level effect records are preserved. Source skill effect code 2500 begins with parameters **100,80,0,0,0,0** at Lv1. The playable DEMO currently interprets only the first 100 as a **2.0× demo damage multiplier**; it does **not** assert this is the exact native damage formula or decode the second 80 parameter. No native spark/elemental/secondary effect/BC logic is claimed.

**Original evolution recipe:** Each 5★→6★ transition requires **500,000 original Zel**, a shared original catalyst item **50354 ×1**, plus four original element-specific catalyst IDs, one each (e.g. Vargas **10130/10131/10132/10133**). The existing demo Evolution Lab button instead charges **10,000 demo Zel** with the exact archived item IDs and quantities displayed alongside the original cost. Demo Lv.2 remains the training threshold for each stage. The shared source-material item **50354** is now granted on each **24th clear of a matching demo quest**, *in addition* to earlier guaranteed 6th/12th/18th-clear rewards; this distribution is DEMO progression and is not presented as an original loot table.

**Four successive evolutions** are now playable on all six starter lines from 2★ through 6★. The current original form is still stored in **`P.evolutions[ownedBaseId]`** under save key **`bf_global_offline_demo_v7`**. No save migration, new fields, inventory reset, roster reroll, or new account/service is introduced. Previous v7 saves and manual JSON backups remain compatible.

**Original sprite caveat:** Archived 6★ sprite sheets range up to **800×800** and use the validated 480×400 animation frame atlas output. Some native layers extend beyond frame borders; they are clipped safely instead of discarded. **Unholy Magress** contains 51 CGG layers with nonzero orientation/reserved flags or fractional scale; exact native orientation-code semantics have not been decoded. The original PNG pixels, source layering order and CGS timestamps are retained, but those frames are not claimed pixel-equivalent to the original mobile client.

**Source and verification:** `source_data/bf_global_six_star_starters_v037.json` and `source_assets/bf1/BF1_Global_2022_Six_Star_Starters.zip.b64` embed source records/source artwork SHA-checked against original 2022 `mst-decoded.zip`, `BF1_unit_part001.zip`, and `BF1_unit_part007.zip`. `prepare_original_six_star_starters.py` is idempotent, source-auditing and fails on shifted HTML anchors. Browser tests verify source names, original stats, all six live evolution actions, four consecutive stages, BB targeting, catalyst rewards, forged save rejection and v7 reload. Final APK tests confirm every source-backed atlas and portrait actually ships offline. APK signing, Home/Quest/Units/Summon, Auto Battle, unit archive and previous BB functionality remain unchanged.

## v0.36 — six other original Global five-star evolutions (60 forms)

Adds the third-stage evolution to all six remaining 3★→4★ character lines. These 2022 Global forms are genuine recovered unit names, stats, portraits, CGG/CGS animated sprite sheets, English Brave Burst names, original target scopes and evolution records.

| Existing playable 4★ form | New playable 5★ form | Recovered BB type |
|---|---|---|
| Fire Beast Zegar #10023 | **Beast King Zegar #10024** | Twin Dragon Slash — single enemy, Injury effect not modeled |
| Dragoon Zephu #20023 | **Dragon Hero Zephu #20024** | Rising Storm — single enemy, Weak effect not modeled |
| Hawkeye Lario #30023 | **Bow God Lario #30024** | Star Gale — all enemies |
| Commander Weiss #40023 | **General Weiss #40024** | Thunder's Order — party ATK support, level-one source parameter **80** over 3 turns |
| Holy Queen Luna #50023 | **Holy Empress Luna #50024** | Savage Stab — all enemies |
| God Blade Mifune #60023 | **Ryujin Mifune #60024** | Cosmic Flash — all enemies |

**Important combat limitation:** The archived five offensive skills use native effect codes **1600, 2300, 3300 and 3400**. Their first numerical values and secondary effects have **not** been proven to mean a conventional damage bonus. Rather than present invented percentages as original rules, the five damaging BBs retain the clearly labeled **2.1× DEMO multiplier** and authentic source-target scopes/first-group hit timing. General Weiss uses the archived Level-1 **80-point ATK-buff parameter** through the existing DEMO interpretation of a party **+80% ATK, three-turn** support buff; buff stacking and round timing are still demo systems. All ten archived BB levels and raw parameters remain stored in the source-backed manifest for future exact mechanics work.

**Evolution:** Each new 5★ source recipe records **200,000 original Zel** and 5 original catalysts, including the special IDs **10191 / 20191 / 30191 / 40191 / 50191 / 60201**. The Evolution Lab continues to charge **7,500 demo Zel**, with the original Zel and material requirements displayed separately. Each 18th clear of an element-matched demo quest now grants its special catalyst, in addition to the previous 6th- and 12th-clear catalyst schedules. These rewards are *not* presented as original enemy drops. All original 18 base recruit IDs, summon pool, quests, existing owned units and prior evolution chains remain unchanged. **60 total playable forms = 18 base + 42 evolved.**

**Original animation:** Six source sprite atlases are baked from hash-verified 2022 PNG and CGG/CGS. The archive contains genuine empty effect frames in Zegar and Mifune, and the source lacks move CGS for Lario and Weiss (the current renderer uses authentic idle sequences as a movement fallback). Lario has five CGG reserved-flag layers with unverified native semantics; its pixel layers are retained but exact effects are not claimed. Original images are never modified.

**Save safety:** No new saved fields, no changes to `bf_global_offline_demo_v7` or Android package ID. An owned base ID retains its currently evolved form in the previous `P.evolutions` mapping. Existing 2★/3★/4★/5★ saves load without migration and arbitrary evolution IDs are still rejected. Battle formation, Auto Battle, UI navigation, and previous BB-support mechanics remain functional.

**Source provenance:** `source_data/bf_global_other_five_star_v036.json`, `source_assets/bf1/BF1_Global_2022_Other_Five_Star.zip.b64`, `prepare_original_other_five_star.py`, and the optional `tools/generate_other_five_star_source_manifest.py` are backed by SHA-verified original 2022 `mst-decoded.zip`, `BF1_unit_part001.zip`, `BF1_unit_part007.zip`. Browser/CI test targeting, evolution, file hashes, save reloads and the compiled APK itself. The browser tests are not a substitute for testing on your Android device.

## v0.35 — all six original Global starters gain playable five-star third evolution

Six further original 2022 Global evolution forms with recovered **English names, source base/Lord stats, original sprite animation atlases, verified 200,000-Zel recipes, and BB target-area records** are integrated into the existing Evolution Lab. The game now offers **18 base recruitable units + 36 evolved forms = 54 playable forms**. Summon selection and owned base IDs do not change.

| Source predecessor (4★) | New playable 5★ form | Archived Brave Burst |
|---|---|---|
| Fire King Vargas #10013 | **Fire God Vargas #10014** | Infinity Nova — 6-hit Fire attack, all enemies |
| Ice Queen Selena #20013 | **Ice Goddess Selena #20014** | Cocytus Zero — 8-hit Water attack, all enemies |
| Earth Pike Lance #30013 | **Nature God Lance #30014** | Eternal Zephyr — 6-hit Earth attack, all enemies |
| Thunder King Eze #40013 | **Thunder God Eze #40014** | Heavenly Thunder — 7-hit Thunder attack, all enemies |
| Holy Knight Atro #50013 | **God Atro #50014** | Messiah Hazzard — 5-hit Light attack, all enemies |
| Black Magress #60013 | **Death Magress #60014** | Vermillion Tower — 6-hit Dark attack, all enemies |

The actual **source evolution requirement** is 200,000 Zel plus one element-appropriate **higher-tier Spirit (e.g. 10133)**, one preceding tier **(10132)**, one **(10131)** and **two (10130)** (corresponding light/dark counterparts use their actual archived IDs). The real offline button charges **7,500 demo Zel** for the third step; earlier 2,500 and 5,000 demo steps are unchanged. All material IDs and amounts are checked against the 2022 evolution master. The existing minimum demo Lv.2 before each evolution still applies.

To make the new source-catalyst requirements attainable without inventing enemy drop tables, every **12th clear of a demo quest** adds one element-matched higher-tier catalyst *in addition to*, not instead of, the existing guaranteed 6th-clear reward. This reward schedule is DEMO behavior, not claimed as original Brave Frontier drop rates.

The source archive provides BB effect code **2500** and original Level 1–10 first numerical parameters **70/80/90/100/110/120/130/140/150/160**, with a separate **60** parameter whose native meaning is not recovered. The existing demo interprets the Level 1 first parameter as **+70% scalar (1.7× prototype damage)**. It is **not a reconstructed native attack formula** or a claim that the second numeric parameter has been decoded. BB hit timestamps and scope are original, but BC, elements, sparking, secondary effects, and original combat formulas still need reconstruction.

Death Magress has 30 archived CGG animation frames, including **22 reduced-scale/orientation-coded layers**. The renderer uses exact source PNG tiles and scale percentages, keeping original layer placement and idle/attack/movement sequences; the native semantics of orientation code 2 are still unknown. We clearly label those affected effects as approximations, not pixel-exact native reproduction.

**Save integrity:** Keeps the existing v7 `bf_global_offline_demo_v7` key and `P.evolutions[ownedBaseId]` mapping. A base unit can evolve successively through 2★ → 3★ → 4★ → 5★ without new saved fields. Saved 3★/4★ units remain valid and invalid unknown evolution IDs continue to be rejected. No existing unlocks or artwork are deleted. The original offline/right-side-player combat and all previous BB/quests/menus remain.

**Source reproducibility:** `source_data/bf_global_six_five_star_v035.json`, `source_assets/bf1/BF1_Global_2022_Six_Five_Star.zip.b64`, and the optionally rerunnable `tools/generate_five_star_source_manifest.py` are SHA-checked against the user's immutable original 2022 `mst-decoded.zip`, `BF1_unit_part001.zip`, and `BF1_unit_part007.zip`. `prepare_original_five_star_starters.py` is idempotent/fail-closed. CI exercises all six evolution actions, live BB targeting, three consecutive stages, v7 save reload, catalog source stats and final **APK-embedded** atlases and portrait files.

## v0.34 — original second-stage Black Magress and the Zegar/Zephu/Lario/Weiss/Luna lines

**18 original recruitable base IDs, 30 evolved forms, 48 playable forms total.** The six additional playable 4★ source-backed Global evolutions are:

| Currently playable 3★ form | Added original 4★ form | Original Brave Burst |
|---|---|---|
| Heavy Magress #60012 | **Black Magress #60013** | Void Pillar — all enemies, BB Lv1 +50% |
| Rage Beast Zegar #10022 | **Fire Beast Zegar #10023** | Hell Twins Attack — single enemy, BB Lv1 +230% |
| Knight Zephu #20022 | **Dragoon Zephu #20023** | Raging Glory — single enemy, BB Lv1 +230% |
| Marksman Lario #30022 | **Hawkeye Lario #30023** | Shooting Star — all enemies, BB Lv1 +60% |
| Strategist Weiss #40022 | **Commander Weiss #40023** | Thunder's Reign — original party ATK +50% for 3 turns |
| Sunshine Luna #50022 | **Holy Queen Luna #50023** | Vulgar Jab — all enemies, BB Lv1 +90% |

These are original 2022 Global unit names, stat blocks, English skill names, target types and first BB-level effect records, not invented new units. The full original BB Level 1–10 modifiers and effect-code metadata remain source-referenced, but only their Level 1 modifier is used during demo battles. The Injury and Weakening secondary effects on Fire Beast Zegar and Dragoon Zephu are **not** simulated because original status-effect formulas are not decoded.

**How to evolve:** The original source requires **100,000 Zel plus the precise recorded elemental catalysts**. The Evolution Lab retains its explicitly labeled 5,000 demo Zel second-step cost, Lv.2 training threshold, and separately displayed original cost. Earlier evolutions are unchanged. The current form remains stored against the player's owned **base ID** in the existing `P.evolutions` map, preserving old save-version **v7** without migration.

**Black Magress rendering:** Archived CGG/CGS/PNG sprites include some 30%/50%/70% pixel-layer scaling and orientation codes 1/2. The new source asset baker honors the recorded percentage scaling using nearest-neighbor sampling and preserves source layer order, idle/attack/movement sequence, and authentic sprite pixels. **Native orientation-code semantics have not yet been established**, so the affected attack effect frames are a reconstruction rather than a claim of perfect pixel-identical native rendering. The base animation frames use unmodified original layers. The original assets are never overwritten.

**Preserved:** All previous 42 forms, original portraits, offline Quest, Unit Box, Evolution Lab, Auto Battle, recovery/support/BB targeting, Mistral and Cave of Flames missions, Android package/signing identity, original combat positions, and the v7 JSON export/import pipeline. No new base summon entries or network requirements.

**Reproducibility:** `source_data/bf_global_more_second_stage_v034.json` and `source_assets/bf1/BF1_Global_2022_More_Second_Stage.zip.b64` embed exactly six source unit sprite sheets, CGG/CGS timing tables and original thumbnails, with SHA-256 checks against the user's immutable `mst-decoded.zip`, `BF1_unit_part001.zip`, and `BF1_unit_part007.zip` archives. `tools/generate_more_second_stage_source_manifest.py` reconstructs the manifest from those archives. `prepare_original_more_second_stage.py` is idempotent and fails closed on unexpected input. Browser regression exercises every form's evolution, source attack/single/party support BB behavior and persisted saves. Android CI verifies source images in the final APK.

**Not yet reconstructed:** native spark logic, elemental relationships, exact original damage formula, original enemy/quest drop tables and status effects; these remain explicitly DEMO.

## v0.33 — six real 4-star second-stage evolutions and chained Evolution Lab

Recover another **six playable original Global forms** by composing source PNG and CGG/CGS animation frames from the immutable 2022 original archives. This brings the current game to **18 original base recruit IDs plus 24 evolved forms = 42 selectable original forms**.

| Existing 3-star form | New playable 4-star form | Archived BB name |
|---|---|---|
| Burning Vargas #10012 | **Fire King Vargas #10013** | Infinity Burst |
| Ice Selena #20012 | **Ice Queen Selena #20013** | Blizzard Pain |
| Vine Pike Lance #30012 | **Earth Pike Lance #30013** | Mystral Rage |
| Thunder Eze #40012 | **Thunder King Eze #40013** | Thunder Retribution |
| Knight Atro #50012 | **Holy Knight Atro #50013** | Thousand Nemesis |
| Samurai Mifune #60022 | **God Blade Mifune #60023** | Aurora Flash |

**Why God Blade Mifune rather than Black Magress?** The 2022 archived 60013 CGG sheet uses extra scales/transformation modes that the validated sprite baker does not yet decode. Mifune's actual Global animation data is complete and supported. Do not substitute a portrait or guess at Magress's missing transformations.

**How to play:** Once you evolve one of these six base units to the above **3-star form**, you can evolve it again in **Units → Evolution Lab** after its demo training reaches Lv.2 and you have the source-listed catalysts. Its second-step archived cost is **100,000 original Zel**, shown for reference. The real offline button currently charges **5,000 demo Zel** for that second step; original drop/economy pacing has not been restored. Both steps keep the same base owned ID and save-format v7 fields. Imported first-stage v7 saves continue to load and can evolve again.

- Original 4-star base/Lord HP/ATK/DEF/REC, element, rarity, cap Lv.60, cost 8, original thumbnail, rendered CGG/CGS idle/movement/attack atlases and exact English names are checked against original source records.
- Six source-listed **all-enemy Brave Bursts**, using archived first-group hit timestamps and **Level 1 modifier** reference: +50% for five starters; God Blade Mifune's Aurora Flash starts at +90%. All ten original BB modifier levels are retained in the source manifest, not automatically unlocked.
- Archive-unverified enemy drops remain labeled demo. The sixth clear of a matching element-index quest now grants one **higher-tier demo catalyst** (IDs 10132/20132/30132/40132/50122/60122). The remaining catalyst schedule is unchanged.
- Existing 36 playable forms and the first-step evolution recipes remain exactly available; no original stats or art replaced. Quest unlocks, summons, previous BB support, combat positions, Auto Battle, menu, and manual JSON saves are retained.
- **v7 is not migrated**: an owned base ID maps to the newest approved evolution form in `P.evolutions`. Parser still rejects unknown owned forms and invalid catalyst data. Prior v7 first-step saves work without conversion.
- Damage formulas, multipliers from secondary effects, source exact turn timing, original economic progression and original battle wave assignments remain unverified DEMO behavior. New skill target scope and Level 1 base modifiers are source-backed; they do not make all game mechanics original.

Provenance: `source_data/bf_global_second_stage_evolutions_v033.json`, source-hashed `source_assets/bf1/BF1_Global_2022_Second_Stage_Evolutions.zip.b64`, audited original `mst-decoded.zip` SHA-256 `69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9`, raw `BF1_unit_part001.zip` and `BF1_unit_part007.zip`. The optional `tools/generate_second_stage_source_manifest.py` regenerates source hashes from the user's archives. The idempotent `prepare_original_second_stage_evolutions.py` rebuilds all new PNG atlases locally. CI verifies both evolution steps, source BB routing, original artwork and final packaged APK.

## v0.32 — six new **playable original** Global evolutions

Restores the full first evolution for all 18 currently recruitable base-unit IDs, instead of limiting evolutions to the previous 12. The six newly playable original 2022 Global forms are:

| Source owned unit | Newly playable evolution | Source Brave Burst |
|---|---|---|
| Warlock Liza (#10041) | **Pyromancer Liza** (#10042) | Meteor Storm — all enemies |
| Healer Merith (#20041) | **Bishop Merith** (#20042) | Cure Storm — party HP |
| Time Mage Claris (#30041) | **Time Lord Claris** (#30042) | Space Ray — party HP (source description) |
| High Dancer May (#40041) | **Royal Dancer May** (#40042) | Healing Samba — party HP |
| Light Lord Mimir (#50041) | **Great Sage Mimir** (#50042) | Star Heal — party HP |
| Magician Lily (#60041) | **Dark Arts Lily** (#60042) | Grand Despair — single enemy; curse status effect not yet simulated |

This raises the game to **18 base playable forms + 18 playable evolved forms = 36 forms** (but only 18 base recruitment IDs, unchanged). Both original and new animation atlases use the archived CGG composition and CGS idle/attack sequences, baked from **exact 2022 source PNGs**. Each form has its own original thumbnail, 2022 English name, base/Lord stats, rarity, cap and cost metadata, and mapped original BB target scope. The four new healer BBs use the original Lv1 **1,000–1,200 HP base range** (unknown REC contribution omitted); Meteor Storm and Grand Despair use their original Lv1 BB +60%/+70% modifier atop explicitly simulated normal damage/DEF. Curse and other secondary effects are **not** invented.

**How to evolve:** Recruit/own the corresponding base unit in the existing demo, earn demo quest catalysts and reach Demo Lv.2 as before, then use **Units → Evolution Lab**. The six new original recipes each require the appropriately colored Nymph ×1 and Spirit ×1 and record **50,000 original Global Zel**. The actual evolution button uses the existing **2,500 demo Zel** price, with both amounts shown separately because original quest drop tables and income pacing are not reconstructed. This price distinction also remains for the older 12 recipes.

**Save compatibility:** Unchanged `bf_global_offline_demo_v7` schema and signing certificate; pre-existing owned units, evolutions, quest progress and stats are not migrated or rewritten. The new six forms are only recorded under their original owned base IDs, using the same existing `P.evolutions` mapping. The six new original BB sources extend the existing archived scope tables without modifying any of the previous 30 verified records.

**Authenticity and safety:** `source_data/bf_global_six_evolutions_v032.json` validates source master records and original CGG/CGS/PNG file hashes; `source_assets/bf1/BF1_Global_2022_Extra_Evolutions.zip.b64` contains only the 6 exact source animation sheets, CGG/CGS files and thumbnails (user archives remain unchanged). `prepare_original_six_evolutions.py` builds real sprite atlases using Pillow in CI, keeps the previous v0.31 identity baseline intact, validates 2022 English BB names/material IDs and fails on unexpected source changes. Browser tests evolve all six forms, exercise all-enemy/single/heal BBs, and load a v7 saved evolved unit after restart. Final APK checks verify every original image and playable metadata entry. This is still a **demo reconstruction**, not a full original Brave Frontier server or full original battle formula implementation.

## v0.31 — original Global names and playable identity references

This update corrects **29 of 30** currently playable form names using the actual **2022 Global English localization** and verifies the entire 30-form current roster against the 2022 `F_UNIT_MST` archive. Most game-screen names were abbreviated or placeholders even though the underlying combat stats were already original.

- Restored exact names throughout **battle, squad setup, owned Unit Box, summons, and evolution screens**. Examples: **Fencer Vargas**, **Pikeman Lance**, **Warrior Eze**, **Beast Zegar**, **Advisor Weiss**, **Archer Lario**, **Healer Merith**, **Burning Vargas**, **Rage Beast Zegar**, **Strategist Weiss**, and **Samurai Mifune**.
- Checked **all 30 source base stats (HP/ATK/DEF/REC)** against current playable unit definitions. Every stat is already a byte-equivalent numeric match; **none was changed**.
- Source `unitMaxLevel` and `unitCost` are now available as read-only metadata. Squad setup displays **DEMO Lv.**, **Original cap Lv.**, and **Original cost** separately so a simulated leveling system is not falsely presented as recovered Global level progression.
- The verified records also preserve original `Lord` stat endpoints for later proper stat-growth implementation, but the game does **not** currently use these endpoints to recalculate combat values.
- The patch **does not add or remove owned units**, alter the 18-base/12-evolved form layout, reroll summons, change equipment/animations, affect combat damage or BB behavior, modify the original quest/enemy data, or write any new save fields.
- Full provenance: `source_data/bf_global_original_playable_identity_v031.json`, directly compared against the hash-verified original 2022 Global catalog (master archive SHA-256 `69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9`). `prepare_original_playable_identity.py` independently cross-validates the 30 names, base stats, source caps, and costs before injecting the UI metadata. It is idempotent and aborts if its source structure differs.
- CI verifies the original names in browser combat and the real Unit Box, source stat equality, zero player-state/save-key changes, full previous regressions, and the **compiled APK** containing all 30 identities.

## v0.30 — source-backed original Global offensive Brave Burst power

In addition to original target scope from v0.28 and support skill Lv1 effects from v0.29, **all 24 offensive BBs** in the playable 30-form roster now apply their source-listed **original Level 1 damage modifiers** on top of the clearly labeled **DEMO** normal damage formula. The former generic `2.1×` multiplier is removed for those known original attacks. Both all-enemy and single-target BBs retain their existing verified scopes and hit-frame distributions.

Original data from `3-mst-translated/F_SKILL_LEVEL_MST_{1..4}_Ver1487.json` inside the authenticated **2022 Global `mst-decoded.zip`** (SHA-256 `69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9`). The original damage-modifier component is taken from the first effect group and audited against original Global English names and targets. Twenty-one skills use archived effect code 1500, one 1800, and two 2000. Separate `@` secondary effect groups are **not** applied, to avoid guessing status-infliction semantics.

- **Vargas — Flare Ride:** original +30% at BB Lv1, increasing to +75% at Lv10.
- **Beast Zegar — Fire Claw Attack:** +150% at Lv1, +240% at Lv10; still single enemy.
- **Marksman Lario — Superior Needle:** +50% at Lv1, +100% at Lv10; still all enemies.
- Source-backed `Lv1–10` power tables for all 24 offensive forms are available in **Units → Unit Box → Original Global Unit Archive → original skill details**. Battle currently uses **Lv1 only**, not an invented leveling progression.
- The active BB gauge and damage preview label show **original Lv1 power**, but base ATK/DEF, variance, elemental relationships, spark, buff interaction and BB charging still use incomplete DEMO mechanics.
- **All six original support skills**, original character profiles, all nine currently implemented archived quests, original sprite atlas, Auto Battle, player-right/enemy-left formation, v7 saves and unchanged Android package/signing remain intact.
- `prepare_original_bb_power.py` is idempotent, validates all 24 skill records and 10 levels each against source-derived JSON, and fails rather than patching unexpected HTML. `tools/verify_original_bb_power_source.py` can independently compare the checked-in manifest against the exact original external 2022 archive.
- Browser tests verify deterministic Lv1 battle damage for 1500/1800/2000 skill categories, normal attacks and no save mutations; APK packaging checks assert all 24 Level 1–10 records and all original art remain shipped offline.

## v0.29 — source-level original Brave Burst support effects

Builds on v0.28's authentic offensive BB targeting. The six support BBs in the currently playable 30 unit forms now use their recovered **type and Level 1 base effect parameters**, rather than using healing for every support skill.

- **Thunder's Command** (unit form **40021**): **+30% ATK** to living allies, lasting **3 demo battle turns**.
- **Thunder's Rage** (unit form **40022**): **+40% ATK** to living allies, lasting **3 demo battle turns**.
- **Cure Light**, **Arcanadia**, **Cure Drill**, **Saint Benediction** (form IDs **20041, 30041, 40041, 50041**): party HP recovery using the archived **Level 1 base range 600–800 HP**, individually capped at missing HP. KO allies cannot be healed into life. These skills do no enemy damage.
- The original ATK percentage and three-turn duration derive from **F_SKILL_LEVEL_MST** level-one effect records `1:1300:0,30,0,0,0,3,90` and `1:1600:0,40,0,0,0,3,90`; healing source records use `1:1500:600,800,50,50`. All 10 recovered skill levels are preserved in `source_data/bf_global_original_bb_support_v029.json` for future original BB leveling.
- **Important limitations:** `50,50` healing REC terms have **not been decoded**, so this implementation uses only the documented base range without claiming the exact original heal formula. Buff stacking priority (higher value wins), cast-round-inclusive expiration, no BB leveling, and battle timing remain **DEMO rules**. The combat log calls this out.
- A visible `ATK +30% / +40%` marker and turns remaining appear on the squad slots. Player outgoing attacks and damaging BBs use the active ATK increase. Enemy attacks and original base stats are not changed.
- Buffs never become saved character data. Reset clears them; expiry automatically makes them ineffective after three demo turns. No changes to your 2022 archives, existing saved schema `bf_global_offline_demo_v7`, roster, summons, quest unlocks, UI navigation, HP rewards or original APK signing.
- The optional regeneration tool `tools/build_global_bb_support_from_archive.py` hashes the exact original decoded master archive and recreates the support manifest from original tables; the Android build uses the committed standalone manifest, never requires a network/Drive connection.
- Existing v0.28 regression now asserts the buff skill **does not** heal, plus a separate browser suite checks buff percentages, duration, damage, recovery, KO exclusions, original targeting, reset, save isolation, and final APK packaging.

## v0.28 — source-verified original BB targeting, demo damage

The original **target scope and BB name** now apply to the 30 already playable demo unit forms. The reference file `source_data/bf_global_original_bb_targeting.json` is cross-checked against **original 2022 Global English Brave Burst descriptions** and the archived `F_SKILL_MST` BB target-area metadata embedded in the existing demo.

- **19 all-enemy offensive BBs** now strike *all living enemies* in the wave, with separately calculated demo damage for each foe. Original first-group hit-frame timing is retained, preserving per-enemy DEF, wave victory handling, and each action's BB gauge reset.
- **5 single-enemy offensive BBs** still strike only the chosen target. The interface names the recovered skill so players can tell its original target type.
- **6 support BBs** still apply the explicitly marked **DEMO SUPPORT healing fallback**, dealing no enemy damage. Their archived effect descriptions remain available in the v0.27 codex, but true effect mechanics are not claimed.
- **Normal attacks** remain single-target; Guard, Auto Battle, target selection, existing simulated enemy waves, victory and rewards, the 34%-per-attack demo BB charge, save schema v7, imported/exported saves, and all Android signing settings are preserved.
- Attack/BB **damage multipliers, buff/debuff effects, targeting for other unfinished units, BC drop generation, original timing tick frequency, and full original hit logic are not reconstructed**. The battle log explicitly labels simulated damage and support effects as DEMO.
- Build-time patch `prepare_original_bb_targeting.py` verifies SHA-256 hashes of the v0.27 source codex and checks all 30 original names, descriptions and BB master target-area fields before changing the bundled HTML. It is idempotent and fails closed if combat source anchors differ.
- CI tests live combat with simultaneous three-enemy targets (AoE vs single vs support), normal attack, BB charging, reset, save integrity, and the final **compiled APK** target manifest.

## v0.27 — archived Global unit stories, skills and exact evolution references

Expands the **original Global encyclopedia** without changing the saved collection or demo combat mechanics:

- Source-derived **1,645 English histories**, **1,659 BB** skill references, **1,424 leader-skill** references, **860 SBB**, **576 UBB**, **571 extra-skill** references, and **1,294 original evolution recipes** across **2,291** archived unit/form records. Entries without recovered English data are omitted rather than fabricated.
- From **Units → Unit Box**, selecting one of your owned demo units now offers **VIEW ORIGINAL GLOBAL PROFILE**. It opens that unit's source profile in the separate encyclopedia. No abilities or evolutions are granted by viewing it.
- In each original profile, collapsible sections show original historical descriptions, ability names/description text and skill IDs, plus original evolution targets, exact source Zel/Karma costs, and source-listed material IDs and counts. Links navigate directly to evolved unit profiles when they exist in the archive.
- Examples: Vargas's original **Flare Ride** and **Fire Spirit's Power**; Natsu Dragneel's **Fire Dragon Slayer Magic** and his source-listed evolution requirements; Sakura Miku's **Sakurafubuki Waltz**.
- Original archives: `mst-decoded.zip` SHA-256 `69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9`; `BF1_sgtext_part001.zip` SHA-256 `4dccce4eeb6a89cc0cf5718badff7af95046c891882e42c05c6eaca81f9d6285`. Local normalization utility: `tools/build_global_unit_codex_from_archives.py` (the large original ZIPs are external user archives, not tracked source).
- HTML includes hash-verified data only; rendering uses `textContent`, not executable skill code. Build-time staging and Android packaging tests verify exact JSON provenance and injection sizes.
- The restored skill text is **not** a claim of original gameplay formula fidelity. Existing offline recruit limit, summons, battles, battle animations, 2022 artwork, nine quests, progression, demo evolution costs, and save schema v7 remain unchanged.

## v0.26: the original Global unit encyclopedia (read-only)

Under **Units → Unit Box → Original Global Unit Archive**, browse the recovered Global database using original **unit/form IDs**, localized names, original stats, leader skill and BB/SBB/UBB ID references, and source-listed evolution targets. This is **not** your owned Unit Box and cannot change the game's summon pools or grant units.

The archived data comes from the user's immutable 2022 Global master archive `mst-decoded.zip` (SHA-256 `69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9`) and original English `BF1_sgtext_part001.zip`. Full coverage: **2,291 unit/form records**, of which **2,252 names** resolve from original Global English, **33** retain a literal master-table name, and **6** remain unlocalized. This includes the special noncollectible Summoner entry and does not imply 2,291 distinct recruitable heroes.

**127 byte-identical original thumbnail PNGs** are extracted from the verified `BF1_unit_part007.zip` and staged in the offline APK, covering early original units and documented crossover examples including Natsu, Erza, Bakugo, Miku and others. Unbundled illustrations are marked **ART PENDING**, not replaced with guesses. Images in `content/unit_archive/` are strictly read-only references. All original source archives remain untouched.

- Search by original name or ID, filter by element, rarity or record type, sort, and page through up to 24 entries at once.
- Tap an entry to inspect base/Lord HP, ATK, DEF and REC, maximum level, cost, original leader/BB/SBB/UBB and extra skill IDs, and archived next evolution IDs.
- Archive IDs and stats are source records only; real combat formulas, effect interpretation, units' ownership, summons, quest waves and full playable roster remain incomplete.
- Retains save schema v7, Android signing identity, all nine quests, music, original artwork, Auto Battle, player-right battle placement, and v0.25 collaboration preview.
- Builds embed verified JSON in the APK's existing HTML to avoid Android offline file:// CORS. Android injects the separate small viewer script because the established UI text reader is limited to 64 KiB per file.
- CI validates the source hashes, 2,291 record count, actual UI search/filter/portrait behavior, no save/roster changes, and the **final APK** containing all 127 original PNG bytes.

## v0.25: source-backed Global collaboration archive preview

- In **Units → Unit Box**, expand **Global Collaboration Archive** for eight documented original Global collaboration entries. Search by name, series or original unit ID; filter by series.
- References include Natsu Dragneel, Erza Scarlet, Acnologia, Katsuki Bakugo, All Might, Mai Shiranui, Legato Bluesummers and Mankai Sakura Miku.
- Data is curated from `BF_Global_Asset_Audit_2026-10-18.md`, which cross-checked `mst-decoded.zip` unit IDs and the `2022APR03-FULL-GL.txt` referenced paths. The original art ZIP bytes are **not** claimed to have been included in this patch.
- **Preview only**: no new owned/recruitable units, actual character sprites, battle stats, skill behavior, summon rates or full collaboration roster. This is an archive index, not a gameplay restoration.
- No save schema, existing roster, battles, quest progression, Auto Battle, Android application ID or signing changes. A dedicated Playwright regression checks search/filter, empty results and save-state invariance.
- Quest encounter joins remain unverified; no unrelated scripted enemies are substituted for normal missions.
- CI workflow now runs the additional browser regression and removes a redundant repeat of mission preparation.

## Authentic 2022 Global battle action artwork

- Original Attack, Guard, and Brave Burst images (normal and disabled artwork), original Auto button variants, battle header/footer, and enemy target mark.
- All 17 PNG files are extracted from original SHA256-verified immutable BF1_battle_part001.zip and BF1__dlcbundle_part001.zip. Archive checksums and PNG dimensions are asserted by prepare_original_battle_controls.py.
- The original HTML battle controls and handler functions are reused, not rewritten: attack, burst, guard, execute, speed, target selection, restart, native Auto checkbox, Auto Battle AI and every save handler remain unchanged.
- The new clickable original-art Auto button calls the already existing checkbox.click(), and synchronizes its aria-pressed label and image with the original Auto state. The checkbox remains visible as a fallback. There is no automatic activation on game launch.
- Original chrome artwork frames the existing battle display and command toolbar. The original target mark decorates the already selected enemy button. These are presentation changes, not new original battle mechanics.

## Preserve existing functionality

- Offline single-player Android package org.bravefrontier.offline; saved progress schema v7 and manual JSON export/import stay unchanged.
- All nine missions through Cave of Flames mission 23, original English Global text, Mistral world map, original optional quest music, Unit Box and evolution previews, original Home navigation, current simulated combat, player's party on RIGHT and enemies on LEFT stay intact.
- Existing battle damage formulas, unit stats/encounters and enemy reward drops are still incomplete demos; this release does not misrepresent them as fully original Global.
- No multiplayer, network service, paid content or automatic Google Drive sync.

## Validation

CI stages 17 exact original PNGs and runs all existing save/combat/navigation/music/map tests plus a browser interaction regression checking native combat command handlers and both original/natural Auto toggle states.
Successful browser/CI verification is not real phone testing. Export a save JSON, then install the same-package APK over the existing app without uninstalling. Preserve the signing key and monotonic versionCode.

## Next

Prioritize source-verified monster-wave mapping, combat effects and native-style battle interaction. Avoid guessing unsupported original damage formulas and encounter composition.
