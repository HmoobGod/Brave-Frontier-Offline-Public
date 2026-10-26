# Brave Frontier Global v75.00 — Original Saint Light #20101 All-Ally Recovery

Parent candidate: v74 source recovery potions commit 8812418ee50ad4b686cc6ea9952de204dcd65d83. Require complete green CI on v74, then exact v75 green APK before promotion.

Recovered and independently SHA256-checked the user-provided 2022 Global translated `F_ITEM_MST_Ver1027.json` row for `聖者の光`, item #20101: effect group 520, skill type 2, target area **2 (all allies)**, exact `passiveSkillInfo: 1000,1000,0,0`, maximum equipped 3 (metadata, not active loadout). This improves source-faithful healing breadth without fictional enemy drops.

v75 adds a compact optional Saint Light command, healing **each living wounded ally** by up to 1000 base HP, never reviving KO units; one charge per battle and actor Guard costs are openly **DEMO-only**. Items #20100 Blessing Light +500, #20000 Potion, #20001 Strong Recovery Potion and #20002 Super Recovery Potion remain separate; this patch does not replace them. The v45 shared reservation ledger blocks multiple item actions by the same unit in a round.

Source effects/target data, Android package, debug signer, no INTERNET permission, unit art, save `P.version=7`, stored inventories and quest clears are unchanged. Browser test validates group capped healing, KO exclusion, shared Guard reservations, independent #20100 charge, modes, resetting and no persistence changes. All inherited tests and signed APK verifier remain required.
