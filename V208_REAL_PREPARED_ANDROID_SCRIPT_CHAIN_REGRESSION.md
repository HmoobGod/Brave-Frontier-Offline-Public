# v208 — Prepared app + complete Android WebView script order smoke test

**Regression-only:** no gameplay, save schema, Android code, signing or
authentic 2022 battle source changes.

Claude's v206 review noted N3: v206 tests previously used a hand-built
HTML shell, not the real 106-quest `index.html` after all build-time
patches, and did not exercise the complete `MainActivity.onPageFinished`
JavaScript injection order or double initialization.

This new Playwright test is executed **after the repository's normal
prepare-HTML step** as part of the existing exact-head Android CI. It:
- Loads the actual 8 MB prepared `index.html` into Chromium, with a
  deterministic empty v7 localStorage mock (no owner's save included).
- Parses the complete `readPackagedText("...js")` sequence from the
  current `MainActivity.onPageFinished` source, asserting each required
  file is staged and the original v149/v151/v206/v174 dependency order.
- Executes the entire Java-equivalent JS script chain **twice**, testing
  repeat `onPageFinished` initialization on the same page.
- Requires v206 Amdahl source guide and downstream v174 crossref module
  to initialize with no JS `pageerror`, with exactly one Amdahl map and
  one guide, seven dungeons and the last dungeon's six missions.
- Requires the same 106 live quests, v7 player state and no
  `localStorage` writes before/after both chains.
- Confirms v206 exported master and quest checksums equal the original
  full 64-character 2022 source evidence.

Unlike v206's stub-page tests, this captures current real prepared
HTML and the entire Java-ordered optional module chain. Unlike a
real-device smoke test, it **cannot** verify actual Android WebView
`onPageFinished` callback behavior, rotation, Android lifecycle,
APK install, owner v124 save migration, or native enemy waves and
drops. Real-device validation remains outstanding.

The patch is **test and CI only**, following separately reviewed/merged
v206, and independent of v207's compiled-APK asset integrity test.
Require exact-head successful full Android CI before merging.
