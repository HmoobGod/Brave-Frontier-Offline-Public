# v188 — Claude-review candidate: opt-in historical BF1 art in read-only unit encyclopedia

**Status: NOT approved / NOT merged / NOT released.** This is the first Android-facing art integration candidate after v183–v187 source retention.

The 54 recovered, per-file SHA256 verified archived BF1 unit portraits are staged to a **separate** APK asset folder `content/unit_historical_archive/`. The original curated 127 thumbnails remain in `content/unit_archive/` and original 2,291 unit catalog records, including their `thumbnail` booleans, remain unchanged.

The existing archive viewer receives a **default-off, session-only checkbox** to display the 54 archived portraits where an original curated portrait is absent, with explicit per-unit text: *Archived BF1 art · exact 2022 Global client revision unverified*. The opt-in never persists through localStorage. Missing image assets fail back to *ART PENDING*. No 2014 enemy formations, 2022-native encounter claims, CGG/CGS animation playback, source AI, damage, drops, quest unlocks, summons, inventory, Gems/Imps, player roster, save version or Android permissions are changed. Only a research encyclopedia image is displayed.

## Archive scope and packaged APK proof

These 54 additional research portraits appear **only in the opt-in unit encyclopedia**. Existing historical wave-lab and enemy preview screens intentionally continue using the original curated art directory; an ART PENDING indicator there is not a regression from this feature. The archive's base counter still refers to **127 curated original Global portraits**, while the opt-in can display 54 separately labeled historical BF1 portraits.

C1 packaged verification: `test_bf_packaged_optional_historical_portraits_v18800.py` runs **after assembleDebug**, inspects the final APK (not merely staging files), and requires byte-identical 54-image ledger coverage, original 127 curated images, the exact 54-ID runtime JS allowlist, default-off checkbox, original 2,291 records, canonical `bf_global_offline_demo_v7`, and no INTERNET permission in the compiled Android manifest. It is registered beside the original packaged unit archive check in `.github/workflows/build-debug-apk.yml`. Green CI is necessary but is **not** Android-device or real-v124-save verification.

## Independent review required before merge

Claude must audit exact source-byte preservation and original asset path separation, source-era labels, the strict 54-ID allowlist, original 127 portraits, 2,291 archive records, missing-image fallback, idempotent event listeners, performance/memory, game/save state isolation, WebView `file://` image loading, Android APK signing, and real owner's v124-save compatibility.

`test_bf_optional_historical_portraits_v18800.py` runs an actual headless Chromium gallery toggle with default-off state, original 127-count parity, recovered real PNG load, visible source warning, no player/S/save changes, and automatic fallback. Existing original 2022/gameplay regressions must remain green. APK packaging verification must be green on the exact candidate head, followed by separate Claude approval **BEFORE MERGE**, then merged-main CI and owner-device smoke test.

**Review checkpoint:** v186 real original 2022 master scan did not verify native enemy formations. v187 discovered one source CGS row with zero final field and 7 nonstandard atlas sizes, so **no archived animation atlas is displayed or animated in this patch**.

**Do not merge this feature PR until Claude returns APPROVE or APPROVE WITH CONDITIONS with all blockers resolved.**
