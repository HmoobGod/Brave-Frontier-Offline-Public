# v263 — Navigation UI screenshot evidence receipts (source level)

**Purpose.** The v259 screen acceptance inventory requires reproducible visual evidence. Source, static image bytes and passing Playwright route tests cannot establish actual 2022 Global visual parity. This patch adds CI-generated, reviewable **navigation-only Chromium** screenshots: real repository `index.html` plus `bf_home_nav.css` / `bf_home_nav.js`, with original art prepared by the existing build pipeline.

**Safe, limited scope.** The script loads **only the source navigation shell** in a fresh, empty, temporary Playwright browser context. Android MainActivity injects many more optional modules in the installed APK, so these screenshots are **not full signed Android WebView captures** and **not original Global screen-matched comparisons**. No device, account, saved-game contents or user data are accessed. No runtime changes, no original-art alteration and no user APK installation.

## Automated capture evidence

- Two representative phone viewports: **320 × 740** and **393 × 852**, DPR 2 and reduced motion.
- Five actual UI routes: **Home, Units, Quest, Summon, Menu**; ten PNG screenshots in total, in viewport-only framing.
- Capture real routed DOM instead of a synthetic mock: main `index.html`, exact source navigation CSS/JS and files in the prepared archive art folder. All HTTP requests are intercepted from a local fake origin; unrecognized hosts are blocked.
- `capture-manifest.json` records route, viewport, image file, SHA-256, file size, document scroll width, route state, no owner save loaded, and missing archive asset references.
- Source regressions guard that route navigation neither changes initial local `P.squad`, `P.gems`, `P.zel` nor changes the temporary v7 browser save value. Fresh contexts per viewport; no personal data is read. Assert visible route surfaces, one active navbar item, no script errors and bounded horizontal overflow.
- GitHub Actions uploads receipts separately as artifact **`BraveFrontier-v263-navigation-screen-receipts`** with 90-day retention, not as an APK. The artifact is for human inspection and manual 2022 comparison only.

## Limitations and acceptance

This evidence may expose image-loading and layout defects but **cannot** establish real Android WebView parity, six-unit actual roster screens, dynamic injected status widgets, complete battle/rendered event overlays, login state, screenshots of the user's v251 install, 2022 original screen reproduction, or native rates/modes. The owner may compare screenshots later; keep **all nine v259 UI surfaces PENDING** until original historical evidence and owner-phone acceptance.

## Dependencies, CI, and safety

Stack v263 onto **v262 PR #196** (head `46b6baa3cc792a1dc5a38f3f667483445635027e`), which depends on v261 #195 → v260 #194 → v259 #193 → v258 #192 → v257 #191 → v256 #190. v256's save/reset UI requires **independent Claude exact-head review** before merging any. After upstream merges, retarget this draft to latest main and rerun source and full Android CI on exact head.

The only changes are a read-only Python screenshot tool, CI path/test/artifact registration and this note. **No** JavaScript, HTML/CSS, Java, Gradle, manifest, package ID, signing, network permission, source artwork, AI, battle, quest, Gems, progression, saved data, save schema or install operation changes. Preserve `org.bravefrontier.offline`, `bf_global_offline_demo_v7`, the installed signed v251 APK and all backups. Completion remains **~65% UI, ~30% full original game** provisional.
