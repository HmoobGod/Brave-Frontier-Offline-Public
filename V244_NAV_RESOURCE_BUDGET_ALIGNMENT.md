# v244 — Align legacy Home navigation byte caps with Android runtime

**Source-only compatibility follow-up to merged v243 (PR #177).** Parent `304bc302cc2bc0fe965f79bca9d4da9ca6cef501`. Draft; independent Claude exact-head review and green exact-head CI required before merge.

## Problem
The four historic dungeon/English quest tests v048–v051 still asserted `len(bf_home_nav.js) < 65536`, despite the current Android `MainActivity.packagedUiResourceLimit()` already permitting up to **128 * 1024 bytes** for *only* `bf_home_nav.js` and `bf_home_nav.css`. v243 was forced to trim a harmless comment to make a 99-byte remaining legacy limit. The loader already rejects sizes >128 KiB for these exact assets, while other UI resources remain limited to 64 KiB.

## Change
- Update the four outdated test bounds to `len(...) <= 128 * 1024` while keeping their source-content and browser/runtime assertions unchanged.
- Add `test_bf_nav_resource_budget_alignment_v24400.py`: independent source gate audits the four assertions, packaged Android limit, nav-only file selection, current nav JS/CSS disk size, full build inclusion, and source preflight inclusion.
- Wire this gate into the dedicated source preflight and full Android APK workflow. Original four legacy tests still run in the full build with their normal prepared assets.

## Safety and boundaries
No changes to `app/src`, Java, CSS, JavaScript, image archives, offline loader, permissions, package/signing identity, v7 save structures, battle/quest rules, Gems, rewards, auto combat or Current. This is **not a visual UI patch** and does not require an owner install. It permits future UI improvements without exceeding the actual Android cap. It does not increase the cap beyond what Android already supports or loosen integrity/parity tests.

## Gates before merge
- Verify exact PR HEAD / base, no drift, and the delta limited to four legacy tests, one v244 gate, two workflows and this document.
- Run the v244 source-only gate; attempt mutation probes that restore a 64 KiB assertion, remove the nav-only loader condition, or allow unrestricted loader bytes.
- Require the dedicated source preflight and exact-head Android APK build to pass, **including the four asset-dependent v048–v051 tests**.
- Independent Claude exact-head review required. No owner device acceptance for source-only changes; v250 remains the planned APK checkpoint.

Known follow-ups from v243: refine Home heading hierarchy and accessible location wording, then visual comparison with original Global reference screenshots. Actual device and save acceptance remains outstanding.
