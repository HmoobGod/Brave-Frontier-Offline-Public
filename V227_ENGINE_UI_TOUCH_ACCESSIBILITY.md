# v227 — Engine/UI touch, focus and reduced-motion acceptance

**Independent engine/UI-only draft on v223 main**, not stacked on v225/v226. v224 mission/item research remains parked. This PR is a presentation and test-only change; it makes no gameplay, engine state, save, enemy AI, reward or inventory modifications.

## Changes

The existing five-button offline navigation shell and its Home buttons receive explicit `touch-action: manipulation`, a 58px minimum height for the five main navigation targets, visible keyboard focus outlines, and reduced-motion timing for **Home and navigation UI only**. It deliberately does not modify Battle animations, global animation speed, battle state, game timers, or save schema.

The new source-only test forbids gameplay selectors or save hooks in the appended CSS, confirms original `BF_homeNav` is unchanged, and requires the Android app to remain without INTERNET permission.

The browser integration test uses installed system Chrome, the real existing navigation bootstrap and CSS, at viewport widths 320, 360, 412 and 540 pixels. It checks five navigable targets at least 44 × 44 CSS pixels and within the viewport, Home/Units/Quest/Summon/Menu switches, exactly one current-route marker, reduced-motion styling, and that P, S and the `bf_global_offline_demo_v7` saved bytes are unchanged, with zero browser storage writes.

## Verification boundaries

Browser and GitHub Android workflows do not substitute for physical Android touch, keyboard focus, screen-reader testing, system font scaling or original-game visual acceptance. At the owner's device gate, verify small-screen tap targets, rotation/portrait, bottom gesture navigation and saved data; don't promote Current until accepted.

v225/v226 are separate navigation and renderer-resilience branches with independent Claude/CI gates. This PR can be reviewed independently but needs a fresh merge-base check if main moves; any conflict or change to the reviewed head needs re-review.
