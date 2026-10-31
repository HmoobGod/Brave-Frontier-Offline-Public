# v232 — Clear stale offline page-load error on an exact packaged main-page restart

**Status:** Draft follow-up, stacked on v231 PR #164 (HEAD `375013cfbd31e2dc76433b32c52acbd505fee9b4`), which follows merged v230. **Not merged or device-tested.**

## Problem
The original v229 failed-page state cleared only when the user tapped "Try again". A future navigation/reload path that starts the same packaged `index.html` could leave `offlinePageLoadFailed` set, preventing `onPageFinished` from injecting the existing Home/nav UI even after a successful load. An older failure dialog could also remain visible.

## Code change
The existing WebViewClient now overrides `onPageStarted` and resets the page-failure flag **only** for `view == game` and the exact `file:///android_asset/index.html` URL; it dismisses the stale page-error dialog. Missing subresources, unrelated URLs and other WebViews do not clear the error flag. `onReceivedError` still sets the flag true for exact failed main-frame loads, and `onPageFinished` still fails closed when a current load has failed. "Try again" and "Close" behavior, renderer recovery, and v231's window-cleanup behavior are unchanged.

Adds `test_bf_offline_page_reload_v23200.py` to both the Android source preflight and full Android build. The test asserts source callback structure/order, not native runtime behavior.

No original data, battle mechanics, quest content, assets, JS/CSS, save keys, signing, Android permissions or app identity change.

## Gates
Require exact-head Android CI plus independent Claude review before merging, in stack order after v231. Real-device tests should include failed main page -> Retry/Close, a separate controlled main-page reload, missing subresource, renderer death, and existing v7 save retention. **Do not promote Current APK without owner device acceptance.**
