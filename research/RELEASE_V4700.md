# Brave Frontier Global v47.00 — Original 2022 Full-HP Revive Item Prototype

Source verified directly from immutable 2022 translated battle item table `3-mst-translated/F_ITEM_MST_Ver1027.json`, SHA-256 `0286402bad6071687a698665e4a12cafdf7aaf9bbc6c131816cd5c2235857474`, inside `mst-decoded.zip`, SHA-256 `69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9`.

Original item **52400** (復活薬) has battleEffectGroupId=610, targetType=1, itemTargetArea=1, skillTypeId=12, passiveSkillInfo=`100`, source max equipped=2, and Japanese description `味方単体の戦闘不能をＨＰ全快の状態で回復する。` — restore one incapacitated ally to full HP. Original #22400 and #22410 also revive but their numeric HP recovery cannot be established solely from their source text, so they are not implemented.

v47 adds an optional archive-battle **DEMO full-HP revival** command. Choose one *living, active, unqueued* actor and one *active but KO* ally. On use the target is set to its current DEMO maxHp, and the actor's turn is reserved under v45–v46's shared item ledger. The revived ally is prevented from gaining a free extra attack in the current DEMO round: actor and newly revived target both Guard at Execute. One temporary charge per battle; mode/round changes reset the in-memory recipient lock appropriately. No real item inventory, saved currency, quest progress, item drop data, or player save bytes are mutated.

**Source-backed**: item identity, original single-ally KO target and complete HP recovery. **Still DEMO**: item availability/stock, act-and-target Guard choice, targeting timing, current-round action lock, original animation and economy.

Retain all v42–v46 tests, verify full/KO eligibility, round lock, cross-item reservation, unsupported modes, unchanged v7 save/Android identity, stable offline debug signer and full packaged regressions. Real device validation is separately pending. Do not promote unless exact commit CI green.
