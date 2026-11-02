# v248 — Original Global Home squad preview, readable on small phones

**Merge checkpoint:** v246 PR #180 and v247 PR #181 are now merged into `main` (v247 main SHA `29f899000c912a84f9edbcf847b5380fa0ce30ed`, exact-head Build #1455 SUCCESS). PR #182 is retargeted to `main`, with this documentation update triggering a fresh exact-head full Android workflow before any v248 merge. The branch originally forked at the earlier v247 commit `40e43e3820c385808d82aec34cbfd92c174c0a5d`; the v247 main merge remains the authoritative checkpoint.

At 320–412px widths, retain all six original Home squad preview slots but display them in three columns over two rows, giving portraits and names meaningful room. Show each unit name at 11px and level at 10px. On wider screens retain the original six-column layout. The existing six-slot render logic, saved squad data, unit order, level values, sprite bytes and game routes are unchanged.

**Only runtime source file modified:** `app/src/main/assets/bf_home_nav.css`. No JS, Java, manifest, network permission, original sprites, battle/AI, save schema, rewards, summons, signing identity or Current user APK changes.

New `test_bf_home_squad_mobile_v24800.py` source and Playwright checks, wired into both the source UI preflight and full Android CI, verify six real DOM squad cards, 3 columns at 320/360/393/412px and 6 at 540px, no overflow, preserved empty-slot accessible labels and original Units route. The preceding v245–247 and save/packaged gates remain active.

To promote: first merge v246 after Android #1440 SUCCESS; then retarget v247 to main and achieve exact-head Android SUCCESS before merge. Then retarget v248 to main, run full Android and preflight on its exact SHA, only then merge. Independent Claude review remains milestone-based at v250 unless significant problems appear.
