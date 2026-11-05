# v228 — Bounded native navigation-resource allowance (engine/UI only)

**Status: draft, not merged, not an APK promotion.** Independent of v225/v226 and v227; based on verified v223 main. The user has restricted new development to engine/UI.

## Verified startup risk

The existing Java `readPackagedText()` reads each packaged UI script with a hard 64 KiB maximum. The 2026-10-30 current committed `bf_home_nav.js` is **65,153 UTF-8 bytes**, just **383 bytes** below that cutoff. A small future UI fix could throw `IOException("Oversized UI resource")` before the Home navigation shell finishes injecting. The original fallback game may still run, but missing menus would be a user-facing regression.

## Correction

- Grant **only** `bf_home_nav.js` and `bf_home_nav.css` a **128 KiB** read allowance, retaining `64 KiB` for every other optional UI resource.
- Preserve the original APK-only `AssetManager.getAssets().open(file)` read path, 4 KiB buffer, strict bounded streaming and UTF-8 decoder.
- No URL/network/file access added, no JS/UI layout edits, no source gameplay, no battle rule, no save/backup/key/schema change.
- Source test `test_bf_engine_ui_asset_budget_v22800.py` checks native allowlist, exact byte sizes, bounded read, manifest no-INTERNET restriction, and preservation of navigation entry point.
- Full Android CI compiles Java and runs the budget test alongside its existing Playwright regressions.

## Follow-up gates

Require green exact-head source CI and Android build, independent Claude code review and guarded merge once existing engine PR order/device acceptance permits. Android device startup, transitions, Home/Quest/Units/Summon/Menu and original saved data still require owner testing before Current promotion. v224 material rewards remain paused. This patch prevents a future size-threshold failure but does not independently prove complete UI/engine authenticity.
