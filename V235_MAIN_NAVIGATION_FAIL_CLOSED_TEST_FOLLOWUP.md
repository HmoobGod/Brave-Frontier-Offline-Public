# v235 — Strengthen native page-load fail-closed source regression (N1–N3)

**Status:** Draft review-only follow-up to **merged v234** on main `082cf17b407b63d4efc278b4e31ac8cbb2e5afea`. No Java, WebView, gameplay, original 2022 source data, manifest, save, assets, signing, or Current APK changes.

## Claude's v234 source review observations addressed

- **N1 — whitespace bypass:** The R1 Retry assertion previously looked for the literal string `offlinePageLoadFailed = false;`; it could miss `offlinePageLoadFailed=false;`. Check the assignment using regex with flexible whitespace and adversarial Retry mutation.
- **N2/N4 — extra resets:** Require exactly one class field initializer and exactly one code assignment to `offlinePageLoadFailed = false` anywhere in MainActivity, with the only assignment inside token-verified `onPageStarted`. Add mutation probes injecting extra clears into `onPageFinished`, renderer recovery, and an unrelated method.
- **N3 — alternate navigation APIs:** Existing exactly-two `.loadUrl(` restriction remains. Forbid additional `.reload(`, `.loadData(`, or `.loadDataWithBaseURL(` calls, and mutation-test them. Preserve the existing `game.goBack()` Android Back route; it cannot itself reset the failure token and must remain functional.

The existing v234 Android-build workflow already invokes `test_bf_offline_main_navigation_token_v23400.py`. Keep that hook unchanged. Add this documentation to source-preflight path triggers. Static tests (including the illustrative callback model) **do not** establish native Android callback timing, source gameplay parity, or real v7 save compatibility.

## Required gates

Independent Claude review of exact PR head, six source preflight workflows and exact-head full Android build successful, then SHA-guarded merge. **Physical-device missing-index, Retry/Close, renderer loss and old v7 save acceptance remain mandatory before Current APK promotion**; no user save editing or APK promotion here.
