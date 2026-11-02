# v244 — Repository-wide Home navigation asset budget alignment

**Status: draft, pending renewed exact-head Claude approval and successful exact-head Android CI.** Parent/base remains merged v243 main `304bc302cc2bc0fe965f79bca9d4da9ca6cef501`. The previous Claude reviews at `c27ce514` and `b73e6cf` both REQUEST CHANGES; neither authorizes merging a newer head.

## Why this patch exists
The already-implemented Android packaged loader allows **128 × 1024 bytes** for precisely `bf_home_nav.js` and `bf_home_nav.css`. Other packaged UI resources still have a **64 × 1024-byte** limit. Source and packaged APK tests had obsolete caps of 65,536 bytes for navigation JavaScript; the nav JS is 65,436 bytes (only 99 bytes below the old test limit).

Claude's first v244 review identified 23 more stale assertions beyond the initial four. A repository-wide AST scan then found 10 additional packaged tests. Claude's second review identified a 38th test, `test_bf_morgan_original_v080.py`, using `(A/'bf_home_nav.js').stat().st_size < 65536`, which the earlier scan missed. That test's bound now uses `<= 128 * 1024`. **All 38 known nav JavaScript size assertions** now match the existing loader cap. No other archive, source, UI or CSS file's 64 KiB cap was broadened.

## Guard against recurrence
`test_bf_nav_resource_budget_alignment_v24400.py` scans every root `test_*.py` file with Python AST and uses scope-aware sequential aliases to distinguish unrelated resource variables. Recognized nav size measurements include `len(nav)`, `len(nav.encode())`, `Path.stat().st_size`, `os.path.getsize(...)`, ZIP `getinfo(...).file_size`, and named size aliases. It resolves simple named integer constants, detects comparisons in `assert`, `if` / `while`, and `unittest.assertLess` or `assertLessEqual`, rejects old limits and OR bypasses, and verifies all 38 known test files still contain the exact `<= 128 * 1024` nav check and remain wired into full APK CI.

The gate includes in-file adversarial probes for these previously omitted syntaxes and preserves valid lower-bound checks such as `0 < len(nav)`. It also validates the **complete exact two-name Java loader selector**, the 128 KiB nav-only cap, the 64 KiB general limit and fail-closed > maxBytes behavior. The v228 gate continues to run alongside it.

## Scope / safeguards
Only existing test files, the v244 test gate, CI workflow registrations and this documentation change. No app/, Java runtime, HTML, CSS, JS, art, Gradle, signing, gameplay, Gems, rewards, save or user Current changes. This is source/test safety work, not a visual or device-accepted gameplay release.

## Merge requirements
1. Reverify PR #178 HEAD and base; previous review reports on different SHAs are not approvals for the current head.
2. Independently review the Morgan one-line change and new gate's measurement syntax, alias scope and adversarial checks. Preserve 64 KiB restrictions for non-navigation UI.
3. Require the exact-head source preflight and full Android APK build to pass, including packaged and asset-dependent legacy tests. A green build on an older SHA does not count.
4. Do not merge until Claude returns APPROVE for the exact current SHA and CI is green. v245 remains next visible UI work; v250 remains the owner's planned APK install checkpoint.

Current personal APK and v7 save have not been edited or independently retested by this change.
