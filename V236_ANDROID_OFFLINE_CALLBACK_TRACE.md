# v236 — Android WebView callback trace: safe device verification

**Status: MERGED SOURCE FEATURE; physical device acceptance is still pending.** v236 PR #169 merged onto v235 main. This is an observational debugging aid, not a native encounter/gameplay patch and not proof of correct Android callback order. Debug tracing is enabled in any debuggable APK built with the v236 source.

## What is recorded

A diagnostic `BFOfflineTrace` tag emits **fixed events**: `initialRequested`, `retryRequested`, `onPageStarted`, `startAccepted`, `onReceivedErrorMain` / `onReceivedErrorSubresource`, `failureLatched`, `onPageFinished`, `injectionAttempt`, `rendererGone`, and `activityDestroy`. Each entry contains only booleans: current WebView identity, exact main-page URL equality (not the URL), whether the native load token is pending, whether the main page failed, and whether the recovery dialog exists.

**No saved progress, unit/inventory contents, full URLs, request/error text, Intent extras or personal data are logged by this helper.** The `FLAG_DEBUGGABLE` guard prevents trace output in a non-debuggable production build, but the existing GitHub Actions workflow builds `assembleDebug`; therefore trace output **is enabled in the ordinary CI APK** once this source is included. Other preexisting Android error logs are unchanged.

## Important installation/saves boundary

The existing `app/build.gradle` uses application ID `org.bravefrontier.offline` for debug builds, with **no** `applicationIdSuffix`, and uses its persistent development debug signing key. Thus a compatible newer APK produced by this workflow will install as an **in-place update to Current**, not a side-by-side test app. The device cannot safely distinguish it as a separate installation. If signing identity differs, Android may refuse the update. **Do not install or overwrite Current without the owner's explicit acceptance and a successful export/backup of the original v7 save.** A backup is not guaranteed merely because APK CI passed.

A side-by-side diagnostic build would need a deliberately different application ID/package and is **not** supplied by v236. That variant would also have separate Android app storage and therefore would not by itself validate the owner's existing real v7 save.

## Normal launch trace on Windows PC

1. **Without installing a new APK**, confirm whether Current already includes v236. If it does not, `BFOfflineTrace` output will be absent; that is expected, not an Android failure.
2. If the owner deliberately approves testing an in-place update, first use the game's existing save/export controls to create a verified backup in a separate location. Record the installed app version and preserve the backed-up file.
3. Install Android Platform Tools on Windows, enable USB debugging, and connect the phone. In PowerShell or Windows Command Prompt, run `adb devices`, then `adb logcat -c`, followed by `adb logcat -s BFOfflineTrace:D`. This command works without Unix single-quote shell syntax.
4. Cold-open Brave Frontier. On a working packaged page, expect `initialRequested` → `onPageStarted` → `startAccepted` → `onPageFinished` → `injectionAttempt`. This means injection was attempted, **not** that user-visible navigation or a saved game is correct. If a subresource fails, `onReceivedErrorSubresource` should not imply a latched main-page failure. Test Home, Android Back, background/resume, and, only if safely reproducible, renderer recovery. Stop logging with Ctrl+C.

## Forced missing-index/error recovery (NOT PROVIDED)

A forced missing or renamed packaged `index.html` requires a **purpose-built altered test APK**, which v236 does not create. If signed with the same app ID and key it would overwrite Current; it must **not** be installed over the owner's saved-game installation as an unapproved test. An isolated application-ID variant avoids an in-place update but cannot directly use the existing in-app v7 storage.

On a properly isolated test environment, record `onPageStarted`, `onReceivedErrorMain`, `failureLatched`, `onPageFinished`, Retry with missing/restored page, Close, duplicate/late callbacks, and renderer loss. Verify the dialog remains visible when the packaged main page fails and that no `injectionAttempt` occurs while failure is latched. To establish existing-save compatibility separately, the owner must authorize a backed-up in-place update and compare the real v7 save before/after.

**Native callback timing, original gameplay fidelity, full APK acceptance and save safety are not established by source tests or CI.** No Current APK promotion follows from this documentation.
