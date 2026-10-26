# Brave Frontier Global v52.00 — Original Double-DEF Battle Item

Based on **verified successful v51.00**, adding original 2022 item #50601 (壁護薬). `mst-decoded.zip` SHA256 `69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9` and translated `F_ITEM_MST_Ver1027.json` SHA256 `0286402bad6071687a698665e4a12cafdf7aaf9bbc6c131816cd5c2235857474` record itemTargetArea=1 and passiveSkillInfo=`0,0,100,0,0,3`. Its Japanese text explicitly describes **doubling one ally's DEF for 3 turns**.

New optional demo command doubles the current unbuffed DEMO DEF for a single living party unit, affects the existing simulated enemy damage formula, and restores exact baseline DEF after three simulated rounds. The older v49 +30% DEF command cannot stack on an active v52 +100% DEF (or vice versa); while the new buff is active its recipient is excluded from both DEF item targeting menus. The v45 shared item-turn ledger charges the actor's DEMO Guard action and existing v48 Auto safeguard remains.

**Original-source backed:** item identity, target, % and 3-turn duration. **Simulated:** one temporary stock, Guard action, rounding, cast-turn timing, stronger effect interaction, DEF combat formula. There is no persistent inventory; no v7 save schema or package/signing identity changes.

Regression gates: source values, action/target legality, v49/v52 nonstacking both directions, expire and exact restoration, simulated damage path, save isolation, archive/training reset, Android APK asset and original key. Do not promote without exact green CI.
