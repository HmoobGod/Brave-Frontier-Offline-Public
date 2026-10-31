# v233 — Fail closed for late WebView page-finished callbacks

Status: DRAFT, stacked on v232 PR #165 exact HEAD `a33538519c84ba1cb4f898d29cb7abb112ffef68`; not merged or Android device-tested.

## Narrow failure mode
After renderer termination, `onRenderProcessGone` destroys the prior WebView and clears `game`. Android callbacks already queued for the old view may still reach `onPageFinished`. v232 checks URL and failed-page state but not WebView identity there. A late callback could attempt JS/CSS injection against a destroyed/replaced WebView.

## Change
Add `if (view != game) return;` immediately after `super.onPageFinished(view, url);` and before the existing exact-URL/failed-load guard and all `evaluateJavascript` calls. Keep all other callbacks, URL guards, navigation, startup Retry/Close, renderer recovery and injected scripts unchanged.

Add `test_bf_stale_webview_finish_guard_v23300.py` to source preflight and full Android workflow; gate verifies the identity guard precedes JS injection and detects guard removal/inversion/order regressions. Static checks do not simulate real Android callback ordering.

No gameplay, assets, manifest, internet permission, signing, storage, save key, localStorage, v7 schema or Current APK changes.

## Gates
1. Merge parent v232 after its own exact-head Android CI, Claude review and merge checks; no Current promotion.
2. Retarget v233 to merged main; verify one-commit five-file incremental delta and exact-head source/Android CI; obtain independent Claude review of the exact final SHA.
3. Owner-device smoke: failed packaged index with callback trace, Retry/Close and successful retry, controlled reload, subresource 404, renderer termination, Android Back and actual old v7 save. Static approval cannot replace device acceptance.
