# Brave Frontier v269 — Unit Box empty and filtered-out screen states

**Source baseline:** merged v268 `main` SHA `6ee27fe0a701fff76a7c9c23d8ff898cb37f400d`. Current owner-installed working APK is v265, and the owner reports existing units, Gems, quests and progress survived the v251 to v265 upgrade. Preserve this app and save.

## Problem

The owned Unit Box previously showed the same "No owned units match this filter." text when the player had no units and when existing units were hidden by a search or filter. It also offered no in-panel reset shortcut for the latter. The screen acceptance inventory v259 explicitly requires empty-list and filter-state evidence.

## Change (presentation only)

In `bf_home_nav.js`:
- Make the existing count a polite status region (same count text).
- When the read-only roster resolves to zero owned units, show **No owned units are available in this offline save.** No action appears.
- When some units exist but no card matches search, squad status, element or rarity filters, show **No owned units match the current filters.** and a keyboard/touch **CLEAR FILTERS** button.
- Clear Filters resets only search, squad-status, element and rarity selectors to all, rerenders from the existing `P.roster`, and returns keyboard focus to the search field. It deliberately preserves the chosen sort order. It never writes `P`, awards rewards or calls save APIs.

In `bf_home_nav.css`: scoped neutral empty-state panel and a minimum 44px reset control with visible keyboard-focus outline. Valid owned-unit cards, portraits, sorting and archived statistics remain unchanged. No new art or fabricated original gameplay is implied.

## Validation

Local 320, 359, 393 and 540px network-blocked Chromium runs using the actual packaged v268 `index.html` plus candidate navigation JS/CSS: **4/4 PASS**. Verified default six owned cards, no-results search and squad reserve filter, reset restoration of all six, preservation of non-filter sort, search focus, 44px target, no-owned presentation with no false reset button, no script error, bounded document overflow, and unchanged synthetic squad/roster/EXP/evolutions/Gems/Zel/Karma/in-memory v7 storage across UI interactions. The no-owned case only modifies a disposable synthetic browser roster before comparing snapshots, never any real saved game.

New `test_bf_unit_box_empty_state_v26900.py` repeats these checks, with `--source-only` guard registered in Android-back UI source preflight and the full test in the signed Android CI. Existing v254 and earlier unit box, portrait and save regression tests remain present.

## Merge and owner safety

Keep PR **DRAFT** until independent Claude exact-head review, all source preflights, full signed PR merge-tree Android CI, verified package/signature and standard APK/identity/diagnostic/fault artifact separation. This is an offline UI patch, not complete original 2022 visual parity or physical Android acceptance. No changes to `index.html`, other game modules, roster, storage key `bf_global_offline_demo_v7`, save parser, quest/combat/recruitment/economy, Android Java/manifest/Gradle/signing, original art archives or network permissions. Do not install over working v265 without separate verified real-save backup and owner device acceptance. UI ~65%, entire 2022 game ~30% provisional; these estimates are unchanged.
