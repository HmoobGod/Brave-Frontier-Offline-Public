# v258 — Global offline UI packaged-image reference audit

**Owner directive:** UI to a measured 100% before adding unrelated gameplay. Existing UI estimate ~65% is preliminary. This v258 milestone introduces objective **original image path completeness** evidence; it does not make the original 2022 Global menus pixel-identical.

**Stacked dependency:** v258 is stacked on v257 PR #191 exact head `3b2dbd2bbefa903603ddf7340e07aa7ae2a8599f`; v257 depends on v256 PR #190, then v255 PR #189. v254 PR #188 is merged at main SHA `9b20af564ef872fb01c81d23a891be25c701e621`. Do not merge v258 until upstream PRs are merged in order and v258 retargeted to main, then exact-head six source preflights and full signed Android CI green.

## Issue and scope

Previously, responsive UI checks often asserted that original Global artwork **filename strings** were present in CSS or JavaScript, but not that the final compiled APK payload contains each image. A missing extracted sprite could therefore leave a visually blank card without failing a layout-only fixture.

`test_bf_ui_asset_paths_v25800.py` extracts unique static `content/...png|jpg|jpeg` references from actual `app/src/main/assets/bf_home_nav.js` and `bf_home_nav.css`. Source-only mode validates reference count (>=35), directories, path safety (no absolute or traversal), loader budgets, no Internet permission, and CI invocation ordering. This runs before original source pack art is materialized, so **no generated file is needed** for source-only preflights.

The second mode runs in the existing **full Android CI** after original BF1 Global menu/battle art preparation. It fails closed if a referenced file is missing/truncated, has wrong PNG/JPEG header/footer, invalid PNG IHDR/dimensions, or implausibly small combined payload. It prints the number of verified static Global UI artworks and total bytes as a build receipt.

This is an audit of **statically referenced navigation and UI artwork** only; runtime portraits, background art selected from a save, and dynamically generated source art require separate audits. Valid file bytes do **not** establish visual placement, owner phone rendering, or original historical pixel fidelity.

## Safety

No runtime app, actual asset bytes, JavaScript/CSS UI, artwork packs, save schema, owner-installed APK, quest data, recruitment or Gem logic, Java, signing or Android permissions are changed. Only a read-only Python test, CI registrations and documentation.

**Merge gates:** exact-head source preflights green; complete Android CI with art preparation and image validation green; preserve all old tests and original source packs. If an image is absent, inspect authenticated art-preparation paths before changing a referenced UI filename; do not invent substitute artwork. Owner v251 install and backup untouched.
