# v234 — One-shot native main-page navigation reset token

**Status:** Draft standalone risk mitigation, stacked on v233 PR #166 (head `6aa6152ad713bf79b27893634bc421b3e3192bbe`); parent #165 v232 still not merged. No device acceptance or Current APK promotion.

## Unresolved v232 risk
v232 resets `offlinePageLoadFailed` on every `onPageStarted` for the exact packaged main-page URL. If Android WebView reports a second start for a failed main-frame navigation after `onReceivedError`, an error page could incorrectly clear the failure flag and allow `onPageFinished` to inject UI into the error document.

## Fix (source-only, fail closed)
Introduce a one-shot `nativeMainLoadRequested` boolean set **before** the initial native `game.loadUrl(...index.html)` and native Retry `failedView.loadUrl(OFFLINE_MAIN_PAGE)` calls. The exact-view/exact-URL `onPageStarted` consumes the token before clearing failure or dismissing the dialog. A duplicate start with no new native request returns without clearing anything. **Retry does not clear `offlinePageLoadFailed` on the button tap**; the old failure stays latched until the one-shot token is consumed by a new exact-page `onPageStarted`, so an old late `onPageFinished` cannot inject the UI between the tap and navigation start. A main-frame error clears the token before setting `offlinePageLoadFailed = true`; renderer loss and Activity destruction also clear it. Missing subresources and unrelated URLs cannot consume the token. A browser/script-only reload following failure deliberately cannot bypass the failure dialog; native Try again remains the recovery path.

The existing exact-view `onPageFinished` identity guard and failed-load guard remain unchanged. No manifest, signing, assets, gameplay, networking, save keys or v7 localStorage changes.

Adds `test_bf_offline_main_navigation_token_v23400.py` (static source contract, comment-resistant guard checks, adversarial mutations for token re-arming, missing error invalidation, premature retry clearing and extra native loads, plus illustrative callback model) to native source-preflight and full Android build. **No Android timing test is claimed.**

## Required gates
- Resolve v232 PR #165, then v233 PR #166, in order with exact-head CI and independent Claude verdicts and head/base delta verification. Retarget this PR to main after parents merge.
- Independent Claude exact-head review of the actual v234 source + adversarial callback semantics.
- Exact-head source CI and full Android CI green; no Current promotion without owner device + v7 save smoke.
- Physical Android debug test with removed/renamed packaged index.html and callback trace: even if duplicate `onPageStarted` follows `onReceivedError`, error dialog stays visible and no injection occurs; then test Try again, Close, successful main page, missing subresource, renderer crash/restart and real v7 save retention.
