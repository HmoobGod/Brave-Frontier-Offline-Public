# v244 — Align all legacy Home navigation byte caps with Android runtime

**Claude review follow-up (B1 remediation) to v244 draft PR #178.** Base: merged v243 main `304bc302cc2bc0fe965f79bca9d4da9ca6cef501`. Re-review exact newest PR HEAD and exact-head CI before merging. Original reviewed head `c27ce514...` received REQUEST CHANGES, superseded by this patch.

## Problem and complete fix
The Android packaged loader already permits up to **128 * 1024 bytes** for `bf_home_nav.js` and `bf_home_nav.css`, and retains a **64 * 1024 byte** limit for all other local UI files. The initial v244 patch updated only four v048–v051 source tests. Claude found 23 more test assertions still imposing the old 64 KiB cap: one source test for original BB power and 22 packaged APK tests, plus 10 additional packaged tests found by the full AST audit. All 37 constrain the navigation asset to the genuine runtime bound `<= 128 * 1024` after this review follow-up. The original BB-power test still retains its independent 64 KiB cap on `archive`; unrelated HTML/script limits are unchanged.

## Regression protection
The v244 source-only gate now parses **every** `test_*.py` file with Python AST. It identifies direct navigation JS/CSS size assertions and assigned variable aliases (e.g. `nav` and APK zip reads), rejects old or too-small ceilings and `or` bypasses, and requires each of the known 37 updated source/packaged tests to retain exactly one 128 KiB assertion and remain included in the full APK CI workflow. New test files are also scanned. It validates the precise whole Java method selecting **only** the two expected nav filenames for the higher cap, plus existing oversize rejection and unchanged 64 KiB general UI limit. Both full Android and dedicated source preflight run the regression gate.

## Safety
Source/test-only patch. No changes to Java, assets, game/quest/battle logic, Gems/rewards, app ID, signing, original images, v7 save compatibility, or Current. It does not change the actual Android loader or promote a device-tested APK. The 37 historical tests still execute in full APK CI with their original gameplay/asset assertions; only the obsolete nav size checks change.

## Merge requirements
- Independent Claude exact-head re-review of **the new head**, including the 23 added test deltas and AST gate, plus adversarial mutation probes for new alias-based tests, `or True`, swapped asset filename, and extra permitted loader names.
- All dedicated source preflights green and full exact-head Android build green, including the old v048–v051 and 22 packaged APK tests.
- Do not merge if PR head moves without re-review. Keep draft pending approval.
- v250 remains the planned owner APK checkpoint; v245 can resume visible Home accessibility UI changes after v244 merge.

Owner's personal Current v124 is historical/not independently rechecked and has not been modified.
