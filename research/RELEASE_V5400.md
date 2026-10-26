# Brave Frontier Global v54.00 — Hope Light (#50100)

Baseline: successful v53.00 Build #266, commit `b3272bcb7e92486af2618f6ceaf5f94c1b0c811d`.

Original 2022 source master `3-mst-translated/F_ITEM_MST_Ver1027.json`, SHA256 `0286402bad6071687a698665e4a12cafdf7aaf9bbc6c131816cd5c2235857474`, in archive `mst-decoded.zip` SHA256 `69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9`. Item **#50100 希望の光** has group 520, all-ally targetArea=2, skillTypeId 2, effect payload `1500,1500,0,0`, max equipped 12, and description `味方全体のＨＰを回復する` (heal entire allied party). The new evidence file also preserves #20100/#50000/#50001.

Optional DEMO battle command: a living unit pays one Guard (v45 shared reservation; v48 Auto protection), all injured living active allies recover up to **1500 DEMO HP each**, capped at maxHp; KO units stay KO. One ephemeral charge per battle; no persistent item inventory, source assets or quest data changed.

Source-backed: name, ID, all-ally scope and raw payload. **Not source-verified:** numerical heal formula, REC, use timing, guarding, temporary item quota, eligibility policy, rounding or animation. The numeric +1500 is a demo approximation, not the original heal formula. Preserve v7 save key, `org.bravefrontier.offline`, stable development signer and all inherited tests. Green exact-commit browser/APK CI required; physical Android test separate.
