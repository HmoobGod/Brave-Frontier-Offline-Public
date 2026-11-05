# v262 — Tactical Focus and live Battle status mobile controls

**Goal:** Continue the Brave Frontier Global offline reconstruction's UI-first track. Make existing optional simulated-combat controls legible, touch-safe and consistent across 320–540px phones. **Not** a native original 2022 Global mechanics or screen-parity claim.

**Stack:** v262 on v261 PR #195 exact parent `91eb1ca84f016b19697065aa9414c58d01147963`; earlier dependencies v260 #194 → v259 #193 → v258 #192 → v257 #191 → v256 #190. Independent Claude exact-head review of v256 destructive/reset control appearance is still required before ANY merge. The whole chain stays draft until upstream sequential merges and retargeted exact-head CI.

## Visual-only changes

Existing v31 Tactical Focus dynamically injects buttons with 42px min height, and v78 Live Battle status dynamically creates a `<details>` summary with 34px min height. The v262 CSS append to `bf_home_nav.css` intentionally outranks the injected defaults without changing those JavaScript modules:
- Tactical **LOWEST HP, HIGHEST ATK, LOWEST DEF, and FOCUS + BB IF READY** controls are at least **50px**, wrap safely, receive keyboard focus styling, and keep existing disabled states and delegated command behavior. Use a 1-column grid at 320–359px and 2-column layout from 360px.
- Battle Status disclosure summary is at least **48px** and visually keyboard accessible. Live status unit names, chips, and footnotes wrap; a genuinely `hidden` status panel stays hidden. The existing `details` open/close semantics are preserved.
- Preserve original background battle art, original action sprites and all v260/v261 selectors.

## Source and browser validation

`test_bf_focus_status_mobile_v26200.py` checks exact scoped CSS, original v31/v78 module identities, CI registration, absence of code/save/network/manifest changes and stylesheet size. A separate simulated **presentation-only** fixture reproduces the *later-injected* v31/v78 styles in headless Chromium at 320/359/360/393/412/540px. It measures computed dimensions, wrapping, no horizontal overflow, disabled focus action, click event, keyboard focus, native disclosure toggle, hidden-state enforcement, and Quest → Home routing.

This test does **not** execute original or DEMO combat, prove damage/AI correctness, inspect v7 storage, run physical-device gestures, compare 2022 archived screenshots or approve Android APK installation. Owner-approved live Battle screenshot parity and the real Android touch experience remain explicit future acceptance gates.

## Critical preservation

No runtime JavaScript modifications; no damage, item, status timing, targeting logic, AI, enemy/npc, rewards, Gem economy, quest state, save schema, replay controls, assets, Java, Gradle, Android manifest or APK signing changes. Preserve `org.bravefrontier.offline`, `bf_global_offline_demo_v7`, installed signed v251 and all existing progress and backups. No automatic install/clear/uninstall. Source CI, signed Android full build and independent review gates are not interchangeable. Completion remains **~65% UI and ~30% whole-game provisional**.
