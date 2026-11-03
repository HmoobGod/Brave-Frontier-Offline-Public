# v268 — Complete unit portrait browser regression

Dependency: v267 PR #202, exact parent c03d5e931bad55e2ee0cf5c3de3e94fd6b5a2e55. Merge v267 first, then rebase this follow-up on final main and recheck the new head.

Claude independently approved v267 but noted that its new automated test covered missing portrait mode mainly in the Unit Box detail and evolution preview. This patch adds a self-contained browser matrix for all four portrait areas: Home squad, Unit Box cards, selected unit detail, evolution preview.

Twelve combinations: widths 320, 359, 393, 540 pixels, each with a valid synthetic image, an empty image source, or corrupted synthetic image data. The test checks expected images or fallback labels, eleven-point readability, unit-specific accessibility labels, whole-line wrapping, containment, no new horizontal overflow, no JavaScript exceptions, and no changes to synthetic roster, squad, evolutions, currencies or in-memory v7 save storage. The source-only test and full local Chromium matrix passed.

Changes are limited to the new Python test, two CI registrations, and this document. Application HTML, JS, CSS, assets, gameplay, Android identity and player data are unchanged. This is a draft stacked test-only change and is not an APK release. Working owner v265 stays untouched. UI estimate 65%, full original game estimate 30%, provisional.
