# v226 — Offline WebView Back timeout and renderer recovery

**Stacked ENGINE/UI-only draft.** This branch starts from the independently Claude-reviewed v225 PR #158, not from merged main. PR #158 must be merged and verified first; keep v224 acquisition research paused. No user Current installation or save is changed.

## Issue and behavior

v225 correctly routes Android Back from in-page Quest/Units/Summon/Menu to Home but keeps `backNavigationPending` true until WebView calls back. If its renderer hangs or exits before the callback, subsequent Back presses are ignored indefinitely.

v226 adds a 2,500 ms main-thread watchdog and a monotonically changing dispatch token. A successful callback cancels the timeout. The timeout restores the old WebView-history/activity Back fallback; a callback arriving after timeout, pause or destruction is ignored rather than triggering a second fallback. A duplicate Back while an active request is pending is still suppressed.

Android's `WebViewClient.onRenderProcessGone` now cleans up only its own WebView, invalidates pending Back, releases an in-progress file chooser, and shows a **native offline recovery dialog**. Restart is user-selected and calls `Activity.recreate()`; Close calls `finish()`. Neither auto-restarts nor deletes local browser data. The dialog explicitly warns unsaved in-memory gameplay may be lost if the user restarts. In-progress back callbacks are cancelled on pause/destroy.

## Verification and limitations

- v225 Chromium route-to-Home/save-immutability regression remains in Android CI.
- New v226 source test checks watchdog, generation guard, renderer cleanup/restart control, unchanged Android permissions and lack of save writes.
- New source preflight runs at exact PR head, Android CI compiles the Java and runs both tests.
- **Not a device-crash simulation.** The source test cannot prove Java callback timing, device back gesture or actual Android renderer failures; manual Android/WebView validation remains necessary.

## Strict non-goals

No changes to browser page, BF_homeNav.js, quest or battle behavior, item economy, rewards, original source assets, data, player/enemy AI, v7 saved key/schema, INTERNET permission, application ID, signing or owner Current APK. The on-screen recovery alert is native UI and does not edit saves.

Never merge v226 before v225 is safely merged and exact-head source + Android CI and independent Claude review are successful.
