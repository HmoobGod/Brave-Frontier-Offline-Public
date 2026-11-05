# v274 — 44px Training controls and visible keyboard focus

## Dependency and safety

This source patch is stacked on v273 PR #208, exact starting head `76d100a8f251865d99b9e46e210768f34b092a71`, which itself depends on v272 PR #207 and v271 PR #206. Merged main at authoring remains v270 `9ea08f2d46413caae09637aa5dbbe84805e140bf`. The required merge order is v271 → v272 → v273 → v274, with downstream retarget/rebase and **fresh exact-head CI and independent Claude review after each upstream merge**. Do not merge this draft over unmerged dependencies.

## UI problem and patch

The actual packaged offline Training card buttons (`+10 EXP`, `+50 EXP ×5`) use CSS `min-height:36px` in the original game's embedded `index.html`. On touch phones, this creates a less forgiving tap target. This patch adds **only** a scoped CSS override to the existing `bf_home_nav.css` for Training card action buttons: minimum **44 CSS px** height, touch-action manipulation, wrapped/legible 12px button font, and a 3px visible keyboard-focus outline with a 2px offset. It does not hide disabled controls or change their labels.

This change applies only when the engine's existing `body.bf-menu-mode` UI is active. **No JavaScript, HTML, Java, manifest, Gradle, signing, art, archived data, app version identity, combat, Training Shards/Zel/EXP, quest rewards, inventory, original Global Fusion behavior or save schema is modified** by this patch. The original Training logic and its disabled-state rules stay authoritative.

## Regression and evidence

New `test_bf_training_touch_focus_v27400.py` checks the committed CSS, workflow registration, offline manifest guard and asset size, then renders the real packaged source `index.html` plus nav JS/CSS in disposable network-blocked Chromium. It checks each of **320, 359, 393 and 540 CSS px** viewports and the default six-unit synthetic roster:

- All 12 demo Training buttons remain present and correctly disabled with the starting zero-resource balance.
- Every Training button has a bounding rectangle at least 44px in both height and width.
- A single button temporarily has only its **DOM disabled property** toggled to test keyboard focus and its 3px solid focus-visible outline. The test never clicks or triggers Training, restores the property immediately, and does not save.
- No new document horizontal overflow or JavaScript errors.
- The synthetic player roster, squad, EXP, evolutions, Gems, Zel, Karma, Training Shards/Used and in-memory `bf_global_offline_demo_v7` value remain identical before/after navigation and focus checks.

A local preflight using signed v273 APK-extracted `index.html` and the exact v273 navigation source plus the v274 CSS override passed **4/4** viewports. The signed Android CI still must validate the final exact PR head. A desktop Chromium test does not certify actual Android WebView touch behavior, TalkBack speech, historical 2022 screen parity, or phone safety.

## Expected diff and merge gates

Expected patch scope versus v273: **five files only** — existing `bf_home_nav.css`, new `test_bf_training_touch_focus_v27400.py`, this document, and two CI workflow registrations. No changes to any shipped gameplay JavaScript or packaged `index.html`. Keep the PR in **DRAFT** until all upstream PRs are independently approved and merged in order, v274 is retargeted/rebased to the final merged main, then **six** source preflights plus full signed Android PR CI (including the old training/game/save tests and all required standard, identity, diagnostic, missing-index artifacts) complete green and independent Claude reviews the **exact final head**. Verify package `org.bravefrontier.offline`, versionCode and signing certificate provenance before promoting.

Owner's working installed v265 and real v7 save are untouched. No install, reset, import, overwrite or owner-phone acceptance was performed. UI restoration ~65% and entire original 2022 game reconstruction ~30% remain provisional and **unchanged** by this mobile control-sizing patch.
