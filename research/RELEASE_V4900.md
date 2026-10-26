# Brave Frontier Global v49.00 — Source-Verified DEF Item

Based on **verified successful v48.00**, with all original unit/quest assets and v7 save compatibility preserved.

Archival provenance: `mst-decoded.zip`, SHA-256 `69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9`; `3-mst-translated/F_ITEM_MST_Ver1027.json`, SHA-256 `0286402bad6071687a698665e4a12cafdf7aaf9bbc6c131816cd5c2235857474`.

2022 source item **#20600 (硬化薬)** has effect group 410, one ally scope, passiveSkillInfo `0,0,30,0,0,3` and a description stating 30% DEF for three turns. This is source-grounded. v49 adds an *optional* battle command that modifies one living ally's **in-memory DEMO DEF** by +30% (nearest integer) for three simulated rounds and then restores exactly the original DEF. The DEMO enemy phase uses the adjusted DEF through its existing damage formula; there is no new combat-engine patch. Single temporary item charge per battle; caster spends the shared item Guard action and cannot double-spend; Auto safety from v48 remains.

DEF buffs do not stack or overwrite another v49 DEF buff. Duration starts with the cast round and expires before the fourth simulated round; native timing, item availability, status math, stacking and combat damage formula remain *unverified DEMO choices*. The evidence file separately records #20601 (+50% one ally), #50600 (+50% all allies) and #50601 (+100% one ally), but these are not enabled.

No persistent inventory, player progress, quest data, storage key, package name or signing material changed. Keep all earlier tests. New browser tests must verify DEF increases during the three simulated rounds, exact restoration upon expiry, blocked item reuse, restart, training mode, and unchanged save bytes. APK test verifies source script and offline debug signing identity. Only promote after exact-commit CI success; Android device check remains separate.
