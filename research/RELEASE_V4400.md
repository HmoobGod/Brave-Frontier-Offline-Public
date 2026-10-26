# Brave Frontier Global v44.00 — Original 2022 ATK Item Prototype

Baseline v43.00 party heal and v42.00 DEMO Potion command, pending full v43 Android verification.

The user's translated **F_ITEM_MST_Ver1027.json** dated 2022 (full file SHA256 **0286402bad6071687a698665e4a12cafdf7aaf9bbc6c131816cd5c2235857474**) records battle item **20400**, raw name **強化薬**, effectGroupId **400**, targetType **1**, itemTargetArea **1**, original itemMaxEquipped **10**, and explicit native text describing **+30% ATK to one ally for three turns**. Unlike potion numeric potency, this amount/duration is directly supported by recovered item source description.

New opt-in live battle command applies this supported numerical boost to one living, previously unbuffed friendly unit through the *existing DEMO* ATK buff system, lasting current round plus two. One temporary item charge per battle; actor's command becomes Guard. Source power and target are original metadata; buff stacking, precise native timing, choice to charge actor's turn, item inventory, status icons and animations remain DEMO and are not represented as original. To avoid inventing stacking, an ally with any active ATK buff cannot receive a second buff.

No P, localStorage, quest progress, summon currencies, saved materials or Android identity mutations by the new module. Save schema remains \`bf_global_offline_demo_v7\`, no INTERNET permission. Full Chromium behavior and signed APK integration tests required; Android physical device QA not claimed.