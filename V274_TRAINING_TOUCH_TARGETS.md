# v274 — 44px Training touch targets and keyboard focus

## Dependency

This source-only UI change is stacked on v273 PR #208 at exact source head `76d100a8f251865d99b9e46e210768f34b092a71`; v273 depends on v272 PR #207, which depends on v271 PR #206. The last merged main remains v270, commit `9ea08f2d46413caae09637aa5dbbe84805e140bf`.

**Required order: v271 → v272 → v273 → v274.** Keep v274 **DRAFT** and do not merge before every upstream patch passes its independent Claude review and signed-CI identity gates and merges; then retarget/rebase v274 to the actual merged main, rerun exact-head CI, and obtain a fresh review.

## Measured problem

The v273 signed APK's real packaged HTML, navigation JS, and CSS expose Training controls that are narrower vertically than useful mobile touch targets: the `+10 EXP` and `+50 EXP ×5` buttons measure **36px high**, the two Training toolbar filters **31px high**, and Training search **29px high**, across widths **320, 359, 393, and 540 CSS px**. Button widths were already sufficient. The disabled state at zero demo resources is correct and should remain unchanged.

## Change — styling only

Append a narrow scoped CSS rule for Training action buttons, toolbar text input and toolbar selects: `box-sizing:border-box;min-height:44px`. Add a consistent **3px visible keyboard focus outline** for the same elements using `:focus-visible`. Do not modify layout outside the existing Training section, create any extra action, change button eligibility or replace resources.

No edits to JavaScript, HTML, original artwork, Android Java/manifest/Gradle, package name, signer, internet permission, demo training prices/caps, unit stats, roster, saved state, Gems, Zel, Karma, battle or rewards. This is a mobile usability and accessibility patch, **not** original 2022 Global Fusion reconstruction.

## Evidence and automated gates

Using **the actual signed v273 APK's** packaged HTML/CSS/JS plus this exact v274 CSS addition, disposable network-blocked Chromium checks at **320 / 359 / 393 / 540px all passed**. Every one of 12 Training action buttons, the Training search field, and two Training selects was at least **44px high and 44px wide** (15 controls total). The search input's computed keyboard focus outline measured 3px, with no new horizontal overflow, JS exceptions, duplicated Training status, changed disabled buttons, or changes in the synthetic roster/squad/EXP/evolutions/Training Shards/Training Spent/Gems/Zel/Karma or in-memory `bf_global_offline_demo_v7` save value. The owner APK and save were never accessed.

New test `test_bf_training_touch_targets_v27400.py` repeats the source-only guard and all four real-page browser widths as part of the signed Android build. The existing v273 Training affordability, v272 evidence, v271 Unit Box, other legacy game/save and UI tests must continue to pass. Source preflight registers the new script and this document. No screenshot files or generated art are committed.

## Promotion conditions

Require independent Claude exact-current-head source and browser **APPROVE**, 6/6 exact-head source preflights, completed signed Android PR build including existing test suites, standard signed APK and v251 identity JSON with matched package/source/merge SHA/versionCode/cert, separately signed diagnostic and missing-index fault APKs, and owner-controlled device acceptance before any installation. An approved review on a superseded SHA is invalid.

Preserve user's working v265 installation and actual v7 save; never install/clear/restore the owner's phone or modify their Gems/units/quests without explicit owner acceptance. The UI completion estimate stays ~65% and full original game ~30% provisional; a touch-target sizing fix does not justify increasing either.
