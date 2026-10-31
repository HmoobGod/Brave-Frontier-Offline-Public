# v236 — Debug-only Android WebView callback trace for owner device verification

**Status: DRAFT.** Stacked directly on merged v235 main `0b7e2f35addbb74b4fe857438d7f07ac4b48d489`. This is a debugging aid to gather actual Android callback order; it does **not** simulate or validate a missing packaged index, fix native callbacks, or change original gameplay.

## What is recorded (debuggable APK only)
A diagnostic `BFOfflineTrace` tag emits named **events**: `initialRequested`, `retryRequested`, `onPageStarted`, `startAccepted`, `onReceivedErrorMain` / `onReceivedErrorSubresource`, `failureLatched`, `onPageFinished`, `injectionAttempt`, `rendererGone`, `activityDestroy`. Each record includes only coarse booleans: current WebView identity, whether the URL equals the exact packaged main URL, one-shot load token pending, main-page failure flag, dialog existence.

**Never logs save payloads, player/unit/inventory state, full URLs, request/error content, Intent extras or account data.** No network, permissions, manifest, JavaScript, original game files, save bridge or save format changes. Debuggable gate prevents new trace lines in a release/non-debuggable build. Existing fixed error `BraveFrontier` logs are unchanged.

## Owner-friendly normal launch trace

1. Install a **separate verified debug APK only after backups and acceptance planning**. Do not overwrite a working Current APK without explicit owner approval.
2. On a PC with Android Platform Tools installed, enable USB debugging and run:
   `adb logcat -c`
   `adb logcat -s BFOfflineTrace:D '*:S'`
3. Open the debug game, then test Home, Android Back, background/resume, and renderer restart if it can be reproduced safely. Stop logcat with Ctrl+C. Expected normal path: `initialRequested`, `onPageStarted`, `startAccepted`, `onPageFinished`, `injectionAttempt`. Missing subresource errors may show `onReceivedErrorSubresource` but must not produce `failureLatched`.

## Critical unverified failure tests

A forced **missing/renamed packaged index.html** requires a **separate non-Current test APK with a deliberately missing asset**; this PR does not claim to generate one. The test must preserve app identity/saves and must never be installed over the owner's working Current without their deliberate consent. Observe exact main error and dialog, duplicate start or late finish, Retry success/failure, Close, renderer loss and recovery; compare real v7 save before/after. Whether these sequences occur is unknown until measured on physical Android.

The Python test is static source verification only. Exact-head Android CI compilation, independent Claude source review and owner device/save acceptance are distinct gates. No Current APK promotion from this PR alone.
