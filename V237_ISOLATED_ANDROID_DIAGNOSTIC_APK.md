# v237 — Isolated diagnostic APK: keep Current installed and untouched

**DRAFT, source/CI candidate.** New Android `diagnostic` build type (based on debug) has application ID **`org.bravefrontier.offline.diagnostic`**, a distinguishable launcher label **`BF Offline Diagnostic`**, and separate Android app storage, distinct from Current's `org.bravefrontier.offline`. Existing `debug` build type, original package ID, signing key, manifest, Java, WebView, JavaScript, game assets and v7 save schema are unchanged.

The `diagnostic` build is explicitly debuggable and shares the development **signing certificate** with the normal debug APK but is a **separate application**, not a compatible update. Its separate localStorage cannot directly read the owner's existing Current app save. **Do not claim this build tests migration/retention of the owner's real v7 save.** It permits safer callback observation on Android without overwriting Current.

## Build and independent binary verification
- Build regular APK and complete the existing original gameplay/save/asset regressions unchanged.
- CI then executes `gradle --no-daemon assembleDiagnostic -PciVersionCode=...` and verifies, with Android SDK `aapt`, regular app ID `org.bravefrontier.offline` vs diagnostic app ID `org.bravefrontier.offline.diagnostic`, distinct diagnostic label, and absence of INTERNET permissions.
- Compare every `assets/` entry, especially packaged index.html, **byte-for-byte** between the two APKs to prove diagnostic mode does not change playable assets, and upload a distinctly named `BraveFrontierOffline-isolated-diagnostic-apk` artifact.
- `test_bf_isolated_diagnostic_build_v23700.py` also runs source-only in the native preflight. Source tests, packaged APK comparison, and physical-device use are separate evidence.

## Owner device workflow
Only after a full successful exact-head Android build and independent Claude review, download the **diagnostic** artifact (not the ordinary debug APK). On Windows with Android Platform Tools: `adb devices`; `adb install app-diagnostic.apk`; `adb shell pm list packages org.bravefrontier.offline` should list **both** packages, and the existing Brave Frontier app should remain installed. Verify the diagnostic app launch label. Run `adb logcat -c` then `adb logcat -s BFOfflineTrace:D` and cold-launch **BF Offline Diagnostic**. Observe `initialRequested`, `onPageStarted`, `startAccepted`, `onPageFinished`, `injectionAttempt`; test Android Back and resume. The logs contain only coarse booleans and event labels.

**Forced failed-index testing is NOT included.** A separately built diagnostic test APK deliberately missing index.html would be required, and must preserve the diagnostic package ID rather than Current's package ID. Owner real-save compatibility must separately be tested, with backed-up save and explicit permission for an in-place update, after the diagnostic functional gates pass. Static/CI success is not a physical device pass or original 2022 gameplay completion.

## Review gates
Claude exact-head code/build/security review, all native source CI and exact-head APK build green, verified separate app ID and original asset equality, then SHA-guarded merge. No installed Current APK, v7 save, or original gameplay changes from this branch.
