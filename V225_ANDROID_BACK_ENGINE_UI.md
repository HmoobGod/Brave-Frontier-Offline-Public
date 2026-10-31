# v225 — Android Back respects in-game navigation (engine/UI only)

**Status:** Draft, pending CI and independent exact-head review. v224 source-only material acquisition research remains parked as open PR #157. This change is independent and based on v223 main.

## Purpose

The offline game uses a single local WebView page with internal Home, Units, Quest, Summon and Menu routes. Android's prior `onBackPressed()` only consulted WebView browser history. Moving among internal routes does not necessarily add WebView history, so Back could unexpectedly close the app instead of returning to the home screen.

Android Back now asks the already-existing `window.BF_homeNav` navigation layer to go Home whenever its current route is not Home. When already at Home, if the navigation module has not loaded, or if the JS callback fails, it falls back to the previous WebView-history / activity-back behavior. A pending-dispatch guard avoids concurrent duplicate Back processing. No new navigation history, save writes or gameplay actions are added.

## Source and behavior checks

- `test_bf_android_back_home_v22500.py --source-only` pins the Android/WebView hook, home route contract and fail-closed callback.
- In the Android Chromium test block, the same test loads the **real existing navigation bootstrap** into a minimal fixture. It checks Quest, Units, Summon and Menu Back-to-Home, Home fall-through, no duplicate UI, absent-navigation fail-closed and no mutations to `P`, `S` or `bf_global_offline_demo_v7` localStorage.
- Android Gradle compilation checks the native Java code. This is an automated browser contract and source/compile gate; actual device Back gesture and user save smoke-testing remain unverified.

## Non-goals and protections

No change to enemy or player combat, quest rewards, original source assets, summon economics, unit inventory, saved data, application ID, package signing, INTERNET permission or WebView file-access settings. No changes to `bf_home_nav.js` or the canonical v7 save schema. This is not a claim of complete original Global engine fidelity.

Merge only after exact-head CI, independent Claude review, and SHA-guarded merge followed by postmerge source + Android workflows. Never promote Current or owner save without device acceptance.
