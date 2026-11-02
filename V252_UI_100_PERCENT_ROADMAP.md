# Brave Frontier Global — UI-only completion roadmap (v252 baseline)

**Owner directive (November 2, 2026): hard-focus development on UI to 100%.** This document defines the UI completion target separately from full original 2022 gameplay reconstruction. The latest installed, owner-smoke-tested build is **v251**; never overwrite the user's existing APK or v7 saves in development.

## Status and definition of 100%

**Estimated UI/engine completion:** ~65%, *provisional and low-confidence*. The older estimate includes substantial underlying navigation work and must not be treated as audited 2022 visual fidelity. **UI 100% must mean** that every agreed offline screen has been inventoried and visually completed using verifiable assets; every displayed control is accurately labeled as working or unavailable; screen navigation, safe-area layout, scrolling, accessibility, and offline rendering pass source tests, responsive browser runs, and owner phone acceptance. Do **not** claim original gameplay parity from UI-only work or turn unavailable game modes into deceptive enabled buttons.

### Auditable UI areas

| Area | Current verified baseline | UI work still required |
| --- | --- | --- |
| Home and squad overview | Original Global source artwork, six squad cards, 320–540px responsiveness, locked-mode nameplates, accessible main headings | Physical phone screenshot vs archived Global source references, visual spacing/icon fidelity |
| Five-route navigation and Android shell | Home, Units, Quest, Summon, Menu/Saves routes; Android Back and renderer recovery; original Global footer/button artwork | Consistent readable titles, focus/heading semantics across every route, device screenshots, safe-area/gesture validation |
| Quest and battle | Offline demo quest path, original art on selected battle/mission UI elements and action buttons, working demo routes | Original screen presentation audit, battle UI/callout hierarchy, player-visible state labels, narrow device overflow |
| Units, Unit Box, squad and evolution | Working demo unit/squad/box navigation and original-image previews | Visual layout and typography parity, controls/state clarity, empty/error states, mobile hit targets |
| Summon and economy UI | Working demo recruitment and Gem information screens | Layout authenticity, offline/demonstration labels, visual parity without changing actual rates or grants |
| Menu, Saves, backup/import | Existing save export/import and offline UI route; v251 owner upgrade saved real progress | Readable save affordances, file import/export error states, documented visual acceptance on device |
| Unavailable original modes | Vortex Gate, Arena, Raid Battle, Capital Randall, Exchange Hall original art-only disabled previews | Truthful, polished preview/shell aesthetics; no fake gameplay, rewards, network or save paths |
| Accessibility and device validation | Source checks and headless Chromium 320/360/393/412/540 widths; v251 real owner upgrade confirmed | Source-authentic comparison references; real Android device screenshots/inspection; complete UI regression inventory |

## v252 — first UI-only patch after v251

Make all **four non-Home routes** (Units, Quest, Summon, Menu/Saves) visibly consistent and accessible without touching underlying demo game logic:

- The existing `#bf-route-title` becomes a level-one accessible heading and polite live label; Home keeps its own main title, so the route heading stays hidden there.
- Style route headings using the previously referenced **original Global battle decorative frame**, maintain text legibility at 320–540px, prevent horizontal clipping, and preserve the exact route names already used by navigation.
- Add `test_bf_global_route_headers_v25200.py` with non-writing source checks and five-viewport Chromium tests; run them in the existing source preflight and full signed Android CI.
- No new asset, original sprites rewritten, Java, Gradle, Android manifest, gameplay/combat, server fetch, Gem economy, save schema, save writes, diagnostic IDs or signing changes.

## Priority and acceptance rules until UI 100%

1. Work **UI-first** in small, reviewed, exact-head patches: Home → navigation/global frame → Quest/battle screen presentation → Units/Box/squad/evolution → Summon → Menu/Saves → disabled original destination previews → device parity and accessibility.
2. For each screen, preserve source-authenticated original art bytes. Show **offline demo / reconstruction** labels where original game services or effects are not recreated. No fabricated original Global quests, Arena, exchange, raids, live summons or rewards.
3. Preserve `org.bravefrontier.offline`, persistent signing, `bf_global_offline_demo_v7`, the existing owner v251 installation and saves. No installation, overwrite, uninstall, data migration or local device modification without separate owner-controlled acceptance.
4. UI progress may move up or **down** after audits. Count not just files or patch numbers but screen inventory and behavior/source-art/physical phone evidence. Keep the overall game's separate ~30% provisional estimate.
5. Every UI PR gets exact-head source preflights, browser coverage and signed Android CI. Independent Claude review when substantial navigation/accessibility state or source fidelity changes warrant it; no merge on failing CI. For major UI milestones compare screenshots on the owner phone before marking visually accepted.
6. Do not restart non-UI original-enemy-wave, quests, Gems, seven-star gameplay or master-database expansion tasks until the UI target is reached, except **essential compatibility/stability fixes** protecting the installed game.

**Milestone boundary:** v252 improves route headings, it does not complete all UI or verify original 2022 device screenshot fidelity. Keep UI ~65% provisional until a screen inventory is actually measured.
