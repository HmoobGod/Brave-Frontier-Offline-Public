# v265 — Real packaged page save/recovery layout regression

## Purpose

Claude independently APPROVED v256 and v264 on exact source heads, with one remaining nonblocking testing limitation: the existing Chromium checks for the recovery backup and destructive New Save use a handmade fixture. Even when it reproduces the original flex basis, it can miss inline CSS rules and real button positioning. The v263 navigation screenshot receipts were likewise **source-navigation-shell-only**, not complete owner-device Android or 2022 parity.

This new test closes that limited **N1 test fidelity gap** without modifying any existing approved UI or reset handler. Its only inputs are the actual committed `app/src/main/assets/index.html`, `bf_home_nav.css`, and `bf_home_nav.js`, in the same way as the existing `test_bf_home_nav.py`.

## Evidence and checks

`test_bf_real_save_page_v26500.py` loads the entire real offline HTML including **all original inline styles** inside an isolated throwaway Chromium profile, adds the actual nav CSS/JS, navigates to Menu, and measures at 320, 359, 360, 393, 412, 540px:

- Real DOM selectors `#downloadsave`, `#quarantineexport`, `#recoverycontinue`, `#wipesave`, `#undosave`, and `#uploadsave`, and real `.transferactions button{flex:1 1 140px}` from inline CSS.
- Both backup controls share the high-contrast gold gradient. Recovery backup and Continue with New Save are 48px minimum (recovery backup 50px at narrow phone widths); the New Save warning appearance differs.
- On wider layouts New Save is a separate 100%-basis row below Undo; narrow pages use a single-column grid.
- No horizontal page overflow or mispositioned action, visible keyboard focus and the original recovery-hidden state remains hidden after simulated visual exposure.
- Never click any backup, import or destructive handler. Check demo `P.squad`, `P.gems`, `P.zel`, and temporary `bf_global_offline_demo_v7` value remain stable through route navigation and visual checks. Browser requests to external HTTP(S) origins are aborted.
- Source-only CI guards required real HTML, CSS, nav, no manifest Internet permission, and registration in both workflows. Full check runs in signed Android build *after* original art preparation.

## Limitations and safety

A real HTML source browser test is stronger than a handmade fixture, but it **is not** an actual installed Android WebView screenshot or original 2022 Global visual comparison; it does not access an owner's account, device, backup, or signed installation. No HTML/JS/CSS/Java/Android/Gradle/art/gameplay/Gem/quest/save logic is changed by v265. Source/test/docs/workflow only. Preserve `org.bravefrontier.offline` and `bf_global_offline_demo_v7`, installed owner signed v251 APK and all saved data.

## Stack

v265 is a draft stacked on v264 PR #198, independently Claude-approved at `3bd812efe84a23e4452339e587762a0b9127e508` and full Android Build #1611 SUCCESS. Upstream v263 PR #197 → v262 #196 → v261 #195 → v260 #194 → v259 #193 → v258 #192. v257 PR #191 MERGED at `72fca1091c95780ddc20bbe50b13f903980ac304`. Continue sequential upstream promotion, exact-head revalidation and signed APK checks. No v265 merge before upstream. Completion estimates remain **~65% UI/~30% full original game, provisional** pending historical 2022 and owner device visual acceptance.
