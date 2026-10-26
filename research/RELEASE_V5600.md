# Brave Frontier Global v56.00 — Original Life Potion (#50000)

Based strictly on the newest successful v55 build (do not start from unverified branches). 2022 `mst-decoded.zip` SHA-256 `69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9`, translated `F_ITEM_MST_Ver1027.json` SHA-256 `0286402bad6071687a698665e4a12cafdf7aaf9bbc6c131816cd5c2235857474`.

Source item **#50000 (生命薬)**, battleEffectGroupId 520, targetType 1, itemTargetArea 1, skillTypeId 2, payload `800,800,0,0`, itemMaxEquipped 10; original description `味方単体のＨＰを少し回復する` states recovery of a small amount of HP to one ally. The master source identifies scope and parameters, not the complete original recovery calculation.

Optional DEMO restores up to 800 HP to one injured active living ally. One temporary item charge and actor Guard enforced by the shared ledger. No healing a KO ally, no exceeding maxHP, no save/inventory writes, no Android identity or signer changes. This is a source-backed item identity and target with **simulated magnitude/turn cost**. Preserve all other modules and regression suites; promote only an exact GitHub Actions green APK.
