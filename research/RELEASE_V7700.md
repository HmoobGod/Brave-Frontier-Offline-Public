# Brave Frontier Global v77.00 — Original Party Regeneration Light

Base: v76 status Nullifier candidate commit 58d9eb02c3dada2670d1b0d7bf275784a883a30b; exact CI success with APK required to promote.

The original 2022 Global `F_ITEM_MST_Ver1027.json` contains `継復光`, item **#20102**, with effectGroup 520, skillTypeId **3**, allied target area **2**, payload **`800,1000,0,3,0`**. Historical community item guides independently confirm this item provides gradual HP restoration **to all allies for three turns** (rather than an instant cure): <https://forum.gamer.com.tw/Co.php?bsn=24641&sn=125267>. The archive does **not** establish whether 800–1000 is rolled per turn, the engine's phase boundaries, REC scaling, or exact healing distribution.

v77 installs an optional additive live `enemyPhase` hook: on use, capture all living active allies, spend one temporary DEMO charge and acting unit Guard (shared v45 ledger); at the end of each of three observed enemy phases, recover up to a **uniform DEMO sample 800–1000 HP** for each surviving injured captured ally. KO allies and replacements are excluded. Each round processes at most once and buffs clear with battle reset. Cast on a full-HP team is still allowed to protect against damage over subsequent turns. Healing before/after Poison and other native timing interactions remain unverified and are clearly labeled simulation.

Source rows are stored in `source_data/bf_global_2022_regeneration_light_v7700.json` with independently checked SHA256. Tests validate three ticks, 800–1000 per tick, cast Guard, no KO revival, stock, duplicate-tick prevention, mode/reset, original #20100 coexistence and P/localStorage isolation. All APK signing, permissions, app ID, saved data version 7, source art and quests preserved.
