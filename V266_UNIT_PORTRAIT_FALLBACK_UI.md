# v266 — Missing original unit portrait UI fallback (presentation only)

**Base:** merged v265 `main` SHA `1dc34cbe069d70c593dc817817c09fce232adcbd`. Installed owner v265 is reported working, including preservation of units, Gems, quests and existing progress. That owner feedback is not a laboratory proof of backup/restore, original 2022 UI parity, or Android signer compatibility. Preserve the working installation.

## Defect and scope

The Home squad tiles, owned Unit Box cards, selected unit details and archived next-evolution preview use original archive `unit.portrait` URLs. A missing/invalid portrait currently produces a blank/broken image; the name/level/stats must remain readable and no original source art should be fabricated.

This v266 UI change adds one `bfOfflineUnitPortraitV266` helper in `bf_home_nav.js`, replacing **only four portrait creation call-sites**. Valid source portrait bytes are still displayed without modification. For missing URLs or an image load/decode error, it replaces the image node with an accessible textual **ART UNAVAILABLE** label. Scoped responsive CSS adds a readable placeholder at 320–540px. No image or asset is replaced in the repository.

## Safety

No change to index.html, P, saveProgress, parseProgress, canonical `bf_global_offline_demo_v7` key, roster/unit identity/rarity/EXP, progression, quests, battles, Gems/Zel, API, Android Java/manifest, signing, Gradle, art archives or package ID. No user data is read, exported, reset, migrated or installed. Keep PR **DRAFT** until independent review and complete CI; do not install any generated APK over the working owner v265.

## Verification

Local disposable Chromium smoke testing using real v265 APK HTML/CSS/JS plus candidate patched presentation completed **12/12 cases**: widths 320, 359, 393 and 540; valid, broken and absent portraits. Tests checked Home, owned Box, selected unit, evolution-preview placeholder, 320–540px overflow and unchanged synthetic P.squad, P.roster, P.evolutions, Gems, Zel, Karma and in-memory v7 save. No real user data involved. This does not verify Android phone rendering, source-archive 2022 parity, or actual backup restoration.

Add `test_bf_unit_portrait_fallback_v26600.py` with source-only and full disposable-browser modes, register it in UI source preflight and signed Android CI. Both current-head CI and an independent exact-head Claude review are needed before promotion. Provisional progress estimates remain **UI ~65%, full original game ~30%**; do not increment by patch number.

## Next gates

Verify 6/6 exact-head source CI plus complete signed Android PR merge-tree and standard/identity vs diagnostic/fault artifacts, correct package/CI signer and offline manifest. Keep v265 owner install untouched. Then, if relevant, capture owner-device screenshots and compare with authentic 2022 reference artwork before UI acceptance.
