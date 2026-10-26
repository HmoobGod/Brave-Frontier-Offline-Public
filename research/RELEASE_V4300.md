# Brave Frontier Global v43.00 — Source-indexed Experimental Party Heal

Baseline: v42.00 optional demo Potion command; build must pass before v43 promotion.

From the user's bundled **2022 translated MST**, file \`3-mst-translated/F_ITEM_MST_Ver1027.json\` SHA-256 **0286402bad6071687a698665e4a12cafdf7aaf9bbc6c131816cd5c2235857474**, source item **20100**, raw name **祝福の光**, uses battleEffectGroupId **520**, targetType **1**, itemTargetArea **2** (all allies), original max equipped **3** and max stack **99**. These are exact original *metadata*, not recovered native healing numbers or executable effect code.

The opt-in DEMO layer inside v42's item panel now offers one separate temporary group-heal charge per battle, restoring **up to 250 synthetic HP to each living injured ally**, excluding KOs. The acting ally's action is forced to Guard during Execute, so using the item costs a player unit turn. Supports cancel/reset by resetting the original battle. No item is added to actual save/inventory, and source battle logic, rewards, world quests and quests remain unchanged. It does not assert matching original item potency, animations, use timings or inventory limits.

Release gates: v42 dependency and Android load order, original source metadata, 6-unit no-revive tests, temporary quota, battle/quest/training boundary, save byte-for-byte equality and all inherited browser/packaged Android regressions. Physical device QA pending.