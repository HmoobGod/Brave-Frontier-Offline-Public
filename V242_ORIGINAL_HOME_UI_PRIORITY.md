# v242 — UI-first: playable Home destinations ahead of recovered locked locations

**Draft; exact-head browser + Android CI and Claude review needed before merge.** This is the first visible UI improvement after the v225–v241 Android diagnostic/stability detour. The user's next phone APK checkpoint remains v250; installed v124 and user save are untouched.

## Actual appearance change

The existing original Global Home location art is **not replaced**. The original Quest and Summoning Hall images now appear together in a clearly labeled **AVAILABLE OFFLINE** row with a larger gold-rimmed playable treatment and wider tap labels. Beneath a separate **RECOVERED GLOBAL LOCATIONS — Artwork preview, not playable** heading, Vortex Gate, Arena, Raid and Randall appear as compact, muted, noninteractive art cards. This repairs the current interleaving of playable Quest and Summon with four locked modes and visually emphasizes working game actions.

Original Game Global sources remain identical: `content/home/home_win_quest.png`, `home_win_akras_smn_hall.png`, `home_win_gate.png`, `home_win_arena.png`, `home_win_raid_open.png` and `home_win_randall.png`. Saved squad overview, Home/Squad/Unit Box/Saves shortcuts, five-button fixed navigation and all game-state APIs are unchanged. No new quest or summon functionality is claimed.

## Acceptance and limits

`test_bf_home_ui_priority_v24200.py --source-only` asserts ordering, original image files, active/inactive distinction, unchanged save-sensitive APIs and size limits. Its Playwright mode checks Home layout and Quest/Summon/Saves actual click routing at **320, 360, 393, 412 and 540px**, plus no horizontal grid overflow or browser exceptions. Run in both source preflight (source mode) and full Android CI (browser mode), retaining existing Android-Back, in-page UI and save/graphics regressions. Browser mocks do not replace actual Android visual acceptance; physical phone screenshots at v250 are still requested. Claude independent exact-head review required, and no owner Current APK update without consent.
