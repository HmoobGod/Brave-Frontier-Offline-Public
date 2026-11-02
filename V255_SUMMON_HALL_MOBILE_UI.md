# v255 — Archived Summoning Hall mobile UI polish

**Stacked base:** v254 PR #188 (head `e7ada79e25067fcbe7d679986f48933ad2e1234c` at the time v255 branched) is stacked on v253 PR #187, which in turn follows merged v252 PR #186. **Do not merge v255 before both v253 and v254 are merged**. After each upstream merge, retarget and recheck the new main-based diff and exact-head source/full Android build.

**Owner directive:** Hard-focus Brave Frontier Global offline UI through a measured 100%. UI progress ~65% provisional; real 2022 source-art visual fidelity is not proven by passing web-browser tests. Owner's v251 APK and save remain untouched.

## Changes

- Render the existing **SUMMONING HALL** banner title as a semantic level-two heading beneath the current non-Home route's level-one heading. Maintain the original Akras Summoning Hall artwork path `content/home/home_win_akras_smn_hall.png` and existing truthful labels: *Offline recruitment prototype* and *No original rates or gacha system are claimed*.
- Improve the banner's responsiveness: shared readable padding and text-wrapping rules, an image constrained to the panel, and a vertical image/text presentation on 320–359px screens. At 360px and wider retain the original row presentation. Do not alter recruitment buttons or Gem handling.
- Register `test_bf_summon_hall_mobile_v25500.py` with the Android Back/UI source preflight and the full signed Android browser test suite. Source checks reject adding save/network changes; Chromium fixture checks six viewport widths, banner/header semantics, original source art linkage, offline disclaimer, responsive layout, usable summon button, route hiding and absence of horizontal overflow.

## Strict boundaries

No new summon rates, original game banners, gem rewards, unit drops, new combat mechanics, save schema, original sprite bytes, Android permissions, Java, Gradle, app signing or package identity. This is UI-only, not proof the original 2022 game's gacha was restored. No user APK installation, overwrite or real save migration.

## Promotion gates

Required: fresh exact-head source preflight tests, full Android Build success on main after stacked dependencies are merged, confirmation of APK artifact and safe scope. A review by Claude becomes required if UI/navigation changes materially affect game state or a substantial visual release milestone is reached. Verify actual Android device appearance with owner's screenshots before claiming UI-screen visual acceptance.
