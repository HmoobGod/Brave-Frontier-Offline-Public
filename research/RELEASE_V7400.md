# Brave Frontier Global v74.00 — Original Stronger Recovery Potions

Base: v73 original Potion ally-target candidate, commit d2bbc21a7c5a06145f1a26c146ea6ff872575e51; do not promote without exact successful APK CI.

Verified directly in the user-provided `mst-decoded.zip`, the translated Global 2022 item table `F_ITEM_MST_Ver1027.json` SHA256 `0286402bad6071687a698665e4a12cafdf7aaf9bbc6c131816cd5c2235857474` identifies **#20001 強回復薬** (1000/1000 base, single ally, max-equipped 7) and **#20002 超回復薬** (2000/2000 base, single ally, max-equipped 5). Both are healing skillType 2/group 520 and share source-known targeting with #20000.

v74 adds a compact expandable original recovery-items control: acting unit separate from living wounded recipient; up to 1000 or 2000 HP capped by missing HP; KO cannot receive. Both original item IDs, potency, scope and item equipped/stack metadata are stored as checked-in source evidence. Each item has one **temporary** charge per battle (DEMO), and actor spends Guard via the existing v45 reservation ledger. No native inventory, item loadout, crafting, recovery coefficient or animation is implied or fabricated. Item stock resets only on fresh battle S.

Inherited v73 original 100–120 Potion, legacy +500 demo Potion, #50000/#50001 recovery and other combat systems remain intact. No Android signing identity, app ID, INTERNET permission, save key/schema, persistent items, source master or unit art is changed. Browser/UI regression and signed APK tests cover both potions, invalid/KO/full targets, independent acting ally, cross-item reservations, reset and save isolation.
