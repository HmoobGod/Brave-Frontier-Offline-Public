# v254 — Unit Box original Global UI mobile clarity

**Verified merged base:** v253 PR #187 source head `d2313ad9375dea84ea7a4b69b5308b31bcc6c839` MERGED into main at `bd39fd94ffeb8a855d5c400ef02ab6370f64dcd5` after six green source preflights and full signed Android Build #1522 SUCCESS (226 successful steps). v254 PR #188 was initially stacked but has now been **retargeted to the current v253 main merge**, preserving its five-file Unit Box-only diff. A fresh exact-head Android CI run is required after this doc change; earlier stacked source checks alone do not authorize merge.

**Owner directive:** Hard-focus UI to 100% before additional original Global content and gameplay changes. UI/engine completion ~65% is provisional, not visual fidelity certification.

## Actual visible changes

The Unit Box already displays the owner's actual units and allows read-only details without changing save data. Improve the **existing** portrait/name cards: show up to two lines of long unit names instead of forcing one-line ellipsis, retain rarity/level and ACTIVE/RESERVE labels, reinforce the already present `aria-pressed` selected state, keyboard focus indication, and detail text wrapping. At widths up to 359px, show two legible columns rather than three cramped columns; retain three columns from 360–519px and four from 520px.

The selected card, roster content, owner squad, archive portrait paths, native UI actions, storage keys, economy, original mission content, and unlocks remain unchanged. No new playable content, JavaScript, manifest, source art, Java/Gradle, signing identity or save schema change.

## Acceptance

`test_bf_unit_box_mobile_v25400.py --source-only` verifies CSS-only use, source art/roster wiring, no save writes/network permissions, and CI registration. Browser mode exercises the real navigation bootstrap with Unit Box card DOM fixtures at **320, 359, 360, 393, 412, 540px**, checking expected 2/3/4 columns, two-line text clamp, keyboard focus, distinct pressed styling, 146px-plus touch cards, no overflow and unchanged Home/Units navigation.

A source/browser fixture does not certify actual roster data, preserved installed game saves, or original 2022 Global screenshot parity. Require exact-head source preflights, signed Android full build, and device visual acceptance where material. If any test fails, do not merge. Owner's v251 APK and real save remain untouched; no automatic install.

## UI next steps

After v254, continue screen-by-screen visual UI audit of Summon, Menu/Saves, battle controls, and archived disabled Global destinations. Re-evaluate the provisional ~65% UI estimate based on authenticated original layouts and real-device screenshots, not patch count.
