# v116 — Original 2022 Unit Base and Lord-Max Stat Evidence

Verified v115 main Build #251 is the parent baseline.

The owner-supplied `mst-decoded.zip` (SHA256 `69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9`) includes exact 2022 `F_UNIT_MST_1/2_Ver1084.json` HP/ATK/DEF/REC stat endpoints for all **72 currently playable forms**. Each row is original `unitBaseHp/Atk/Def/Rec` (level-one) and `unitLordHp/Atk/Def/Rec` (original Lord form at `unitMaxLevel`) with `unitExpPatternId`. A separately verified `F_UNIT_TYPE_MST_Ver52.json` provides **six** original type modifier raw ranges; exact field strings and source hashes are retained.

Notable verified rows: unit #10011 starts at HP 1030, ATK 500, DEF 410, REC 320; Lord max level 12: HP 1948, ATK 700, DEF 574, REC 448. Unit #10015 original max level 100, Lord HP 5313. These are source-derived data, not estimates.

### Current implementation boundary

**Read-only.** The generated APK embeds all 72 × (4 base + 4 Lord-max stats), six original type modifier records, and SHA256 provenance. The collapsed Squad Setup panel displays the selected unit forms and their original level-one and Lord-max stats. The endpoint lookup deliberately returns null for other levels, so it cannot pass off an interpolated DEMO stat as the original 2022 formula.

The v115 original maximum-level cap and v111/v113 source-matched leader buffs continue running exactly as before. No changes to battle HP/ATK/DEF/REC, original stat-type selection, EXP thresholds, saved version-7 progress, Android package/signing, quest rewards, Energy or item drops.

### Next original mechanics step

Determine and independently test the original **in-between-level stat formula** and Lord/Anima/Breaker/Guardian/Oracle type-stat placement from original sources. Only then modify the playerUnit construction path, preserving level caps before leader bonuses and validating no regressions in save, training, battle initialization, evolution and existing QoL features.
