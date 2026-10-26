# Brave Frontier Global v46.00 — Source-Verified BB Gauge Item Prototype

Baseline: v45.00 shared item-turn reservations (must be exactly green in GitHub Actions before promotion). Original source archive: `mst-decoded.zip`, SHA-256 `69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9`. Verified inner translated table: `3-mst-translated/F_ITEM_MST_Ver1027.json`, SHA-256 `0286402bad6071687a698665e4a12cafdf7aaf9bbc6c131816cd5c2235857474`, 1,668 item rows.

Original source item **21000** raw name **武神薬** has battleEffectGroupId=540, targetType=1, itemTargetArea=1, skillTypeId=4, passiveSkillInfo=`0,100`, max equipped 2, original Japanese description `味方単体のＢＢゲージを最大にする` (max out a single ally BB gauge). Item **21010** (武神薬改) has the same described effect and source parameters but max equipped 3. This is an original source-backed *effect and target*, not proof of the original timing, turn cost, inventory or buff behavior.

v46 adds an optional active-battle command: choose one living actor and another (or same) living active unit with an incomplete BB gauge; set recipient's existing demo BB meter to 100. One temporary per-battle charge; actor's DEMO command becomes Guard and is registered with v45 cross-item reservation. Full gauge, KO, busy, auto, finished and training use are rejected. This prototype neither grants nor consumes real saved inventory and never changes `P`, `bf_global_offline_demo_v7`, campaign quest data, item rewards or build signer.

The accompanying immutable evidence JSON includes the five item rows' exact source parameters and explicitly distinguishes descriptions from undecoded effect math. For #20100, `500,500,0,0` is now recorded, but **its native numeric healing formula remains unverified**; the existing +250 DEMO party heal is left unchanged. v42 Potion also remains synthetic and unchanged.

Release gates: Chromium source metadata, target/actor legality, BB gauge effect, Guard reservation shared with other temporary items, save-byte equality, charge reset, original v42-v45 regression retention, and signed/offline packaged APK checks. Physical Android QA must be reported separately.
