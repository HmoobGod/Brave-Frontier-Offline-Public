# v275 — Training search/filter 44px phone controls

## Dependency and reconciliation

**This is a focused follow-up to v274 PR #209**, exact source HEAD `e0d6ab433152550c6d0e6749289f0a5e6258b03d`, on branch `feature/v274-training-touch-focus`. The PR #209 patch already fixes the two Training action buttons' 36px touch height and button focus styling. A separate concurrent attempt, PR #211, overlapped that work. This v275 adds **only the missing Training search and two filter/select targets**, on top of the existing v274 branch, avoiding duplicate button styles.

The canonical source stack is v271 PR #206 → v272 PR #207 → v273 PR #208 → v274 PR #209 → **v275**. Other concurrent alternative v273 PR #210 is not a prerequisite for this stack and must be reconciled separately. The last verified merged main is v270 SHA `9ea08f2d46413caae09637aa5dbbe84805e140bf`. No PR may merge out of order.

## Measured problem and change

The actual v273 signed Android APK's packaged HTML/JS/CSS showed Training search input **29px** high and two Training filter/sort selects **31px** high across 320, 359, 393 and 540 CSS-pixel browser widths. The v274 PR #209 raises the Training action buttons to 44px with 12px readable button labels, but leaves these three form fields short.

Append narrow Training-toolbar-only CSS to set `box-sizing:border-box;min-height:44px` on one search input and both selects. Add a consistent, 3px, `:focus-visible` keyboard outline for these fields. Do not modify the Training action buttons: v274 PR #209 owns those changes. Do not change labels, layout outside Training, gameplay, existing affordability note, saved data, or resource eligibility.

## Exact scope

Expected five changed files relative to v274 PR #209: **one CSS addition** to `app/src/main/assets/bf_home_nav.css`, new `test_bf_training_form_targets_v27500.py`, this document, and source-preflight/build workflow registrations. No edits to JS, `index.html`, art, quests, battle, Training Shards, Zel, unit stats, saved roster/v7 schema, Java, Gradle, manifest, signer or Internet permission. This is UI sizing/accessibility evidence, **not** restoration of original 2022 Global gameplay.

## Local validation

In disposable network-blocked Chromium, the real signed v273 APK packaged HTML/JS plus v274 PR #209 CSS and this exact v275 CSS were checked at **320 / 359 / 393 / 540px**. **All 4/4 widths PASS:** the Training search, both selectors and all twelve existing action buttons are at least **44px wide and high** (15 controls total); 3px solid focus outline appears when keyboard-focus is assigned to input/select; 12px button label styling from v274 remains intact. No additional horizontal overflow, browser exceptions or changes to synthetic roster/squad/EXP/evolutions/Gems/Zel/Karma/Training counts or in-memory `bf_global_offline_demo_v7`. No real owner device/save was used.

New `test_bf_training_form_targets_v27500.py` repeats these checks against actual packaged assets in source and signed Android CI. Native TalkBack and historical screenshot comparison remain pending.

## Promotion gates

Keep **DRAFT** until v271→v274 are individually approved, signed-CI verified, merged in order, and v275 rebased/retargeted to actual merged main. Obtain independent Claude **exact final HEAD** approval, six source preflights, signed Android CI including all legacy game/save tests and signed APK/identity/diagnostic/fault artifacts before merge. Do not change the user's installed working v265 APK or its saved units, quests, Gems, or local v7 save without a verified owner-controlled backup and explicit installation acceptance.

UI reconstruction estimate ~65%, full original game reconstruction ~30%; provisional and unchanged by this form-size patch.
