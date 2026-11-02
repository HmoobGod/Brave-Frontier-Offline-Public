# v256 — Menu/Saves backup and destructive-reset visual safety

**Owner UI priority:** hard-focus original Brave Frontier Global offline interface to a measured 100% while preserving the real installed v251 and its locally backed-up progress. Current UI/engine estimate ~65% provisional, not a claim of original 2022 screenshot fidelity.

**Stacking:** v256 is based on v255 PR #189, which depends on v254 PR #188, then v253 PR #187, following merged v252 PR #186. **Do not merge v256 before upstream PRs are merged and this PR is retargeted to current main with fresh exact-head Android CI.**

## Why the UI needs this patch

An inspection of the packaged **v251** WebView HTML and CSS (isolated test environment, not owner's phone or save data) found that `Download Save File` and `New Save` were presented as similarly weighted controls in the Menu/Saves panel. That risks accidental misrecognition during normal backups, even though existing reset confirmation and save-recovery safeguards remain unchanged.

## Actual UI changes (CSS-only)

- Give **Download Save File** a brighter gold-framed export/backup appearance. It remains the same existing functional button.
- Give existing **New Save** (`#wipesave`) and recovery-mode **Continue with New Save** (`#recoverycontinue`) distinct warning-colored styling so visually they cannot be mistaken for routine export/import.
- Keep labels, button IDs, click/confirmation handlers, backup and import functionality, save format, existing local storage keys and all recovery guards **unchanged**.
- On phones 320–359px wide, make the six backup/import controls a single-column grid with legible wrapped labels and 50px minimum touch targets. At larger widths retain the current arrangement. Add visible keyboard focus styling.

## Tests

`test_bf_save_controls_mobile_v25600.py` checks the modified CSS selectors, minimum touch sizing, differences between backup and reset controls, focus states, narrow-screen column count, route visibility and no overflow at 320/359/360/393/412/540px. Source-only guards verify no modified save/event logic or network/permissions and size budgets. Browser tests use representative button DOM whose IDs/labels were independently read from the v251 packaged `index.html`; fixture results are not an owner's real-save or actual Android device test.

## Review and promotion gates

This UI work makes potentially destructive controls more conspicuous, but it must not alter the actual reset confirmation or action. **Request Claude exact-head independent review before merging v256** to verify both preservation of the existing save handlers and proper separation of visual vs behavioral changes. Require upstream merges, current-main retargeting, all six source preflights, full signed Android CI and owner device appearance acceptance at next install checkpoint. Do not auto-install or overwrite the owner's current APK.
