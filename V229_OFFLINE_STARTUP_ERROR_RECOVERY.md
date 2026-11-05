# v229 — Native recovery when the packaged offline main page fails to load

**ENGINE/UI ONLY — draft, stacked on v226 PR #159.** Not merged or installed. Main remains v223; v224 original material-acquisition research is on hold.

## Symptom

When `file:///android_asset/index.html` fails to load as the main document, Android's WebView can display a generic error page without a game-appropriate way to recover. v226 already addresses renderer termination, not ordinary main-document load errors.

## Native behavior

- `onReceivedError` handles only errors for **this game's WebView** that are **main-frame requests** with the exact packaged index URL. Failures of secondary images, optional assets and unrelated URLs are ignored.
- One non-cancelable native **Offline game could not start** dialog explains the bundled page could not open. **Try again** clears the failed flag and reloads exactly the packaged index; **Close** finishes the activity.
- `onPageFinished` does not inject navigation scripts into a page known to have failed; after retry it may initialize the normal page.
- If the renderer exits while a load error dialog is visible, v226's renderer recovery path dismisses the old dialog first. The native startup dialog is also dismissed on activity destruction.
- No user save is imported, exported, overwritten or reset as part of recovery. Unsaved in-memory actions may still be lost if the activity exits or the renderer crashes.

## Tests and limits

`test_bf_offline_page_recovery_v22900.py` validates the main-frame and exact-URL guards, retry/close behavior, error-page script injection guard, renderer cleanup, and absence of save/network changes. Existing v225 browser navigation and v226 renderer recovery tests still run in Android CI. The source preflight checks only static contracts; compiled Android and device testing are required.

**Device acceptance not yet performed:** force a main document load error in a debug emulator or test APK, confirm one retry dialog, retry and normal Home launch, no false prompts for missing subresources, WebView renderer crash behavior, Android Back, and preservation of an existing v7 save. Do not promote Current without owner acceptance.

The patch does not alter `bf_home_nav.js`, combat, rewards, inventory, original AI, save key `bf_global_offline_demo_v7`, INTERNET permission, packaging, signing or app ID.

Merge only after v225 and v226 are safely integrated, exact-head source+Android CI are green, and an independent Claude exact-head review approves this stacked delta.
