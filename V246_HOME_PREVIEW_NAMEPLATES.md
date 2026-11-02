# v246 — Visible nameplates for recovered Original Global locations

**Base:** v245 merged main `cd8ddbd1569cbb3850a7bf2d799f71aa33a9a432`.

The Home's four recovered Global destination art previews already communicated their locations to screen readers but all showed only **NOT YET AVAILABLE** visibly. This small UI-only change adds clearly legible visible nameplates: **VORTEX GATE, ARENA, RAID BATTLE, CAPITAL RANDALL**, each above its unchanged NOT YET AVAILABLE status. Labels are `aria-hidden` to prevent duplicating the existing `aria-label="<location> not implemented"` on the surrounding disabled `role="group"` container. Quest and Summon remain playable demo destinations; these four locations remain genuinely unavailable and noninteractive. Neither new navigation, placeholder screens, online functionality nor gameplay capability is implied.

Scope: `bf_home_nav.js`, `bf_home_nav.css`, one source + Chromium responsive test, CI wiring and this document. Original sprites and source archives unchanged. Preserve all Java/manifest/Gradle, v7 saves and Current, rewards, summons, combat, battle AI, navigation, offline behavior, package ID and APK signing.

`test_bf_home_preview_nameplates_v24600.py` checks four original asset paths/names, no clickable/focusable locked cards, maintained 128 KiB nav resource budget, no save writes or Internet permission. Headless Chromium verifies visible names, readable >=10px font, non-clipped cards/grid and unchanged Quest/Summon routing at 320, 360, 393, 412 and 540px. Runs source-only in the dedicated UI preflight and full browser tests in the Android APK workflow.

Release plan: if all exact-head source and Android CI gates pass, merge as low-risk UI without a separate Claude pass; request independent Claude at v250 or if a substantive regression arises. Do not treat CI as physical-device acceptance; user install checkpoint remains v250.
