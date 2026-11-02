# v248 — Original Global Home squad preview, readable on small phones

**Stacked dependency:** based on v247 PR #181 HEAD `40e43e3820c385808d82aec34cbfd92c174c0a5d`, which itself includes v246 PR #180. This is an experimental UI branch; **do not merge v248 before v246 and v247 are merged with exact-head Android CI green**.

At 320–412px widths, retain all six original Home squad preview slots but display them in three columns over two rows, giving portraits and names meaningful room. Show each unit name at 11px and level at 10px. On wider screens retain the original six-column layout. The existing six-slot render logic, saved squad data, unit order, level values, sprite bytes and game routes are unchanged.

**Only runtime source file modified:** `app/src/main/assets/bf_home_nav.css`. No JS, Java, manifest, network permission, original sprites, battle/AI, save schema, rewards, summons, signing identity or Current user APK changes.

New `test_bf_home_squad_mobile_v24800.py` source and Playwright checks, wired into both the source UI preflight and full Android CI, verify six real DOM squad cards, 3 columns at 320/360/393/412px and 6 at 540px, no overflow, preserved empty-slot accessible labels and original Units route. The preceding v245–247 and save/packaged gates remain active.

To promote: first merge v246 after Android #1440 SUCCESS; then retarget v247 to main and achieve exact-head Android SUCCESS before merge. Then retarget v248 to main, run full Android and preflight on its exact SHA, only then merge. Independent Claude review remains milestone-based at v250 unless significant problems appear.
