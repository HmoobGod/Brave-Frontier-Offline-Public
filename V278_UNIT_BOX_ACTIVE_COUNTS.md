# v278 — Unit Box truthful active squad counts and unavailable-profile detail

**Parent:** canonical v277 PR #214 source HEAD `73f7959d78055e93445abd5eff03790713377599`. **Status:** draft-only; merged main still v272 at `7f338bce12a09de61b81189c2885e95ed099b63f`. Do not merge before v273 PR #208 → v274 #209 → v275 #212 → v276 #213 → v277 #214 each completes ordered promotion.

## Why

Claude's independent v271 source/browser review APPROVED with no blockers but noted two presentation ambiguities (N1 and N2):

- **N1:** Unit Box count called every squad ID "active" even if that saved ID has no archive display profile. For example, one resolved squad member plus one unresolved roster ID could report "2 active".
- **N2:** When every saved roster ID is unresolved, the Unit Box detail panel says "Select an owned unit" despite having no selectable unit cards.

These are defensive presentation states. Valid v7 parser paths generally reject unknown IDs, so do **not** treat synthetic bad IDs as a real-save migration, content recovery or original Global feature.

## Exact change

Only `app/src/main/assets/bf_home_nav.js` changes at runtime, and only inside the existing Unit Box renderer:

1. Derive `resolvedIds` from already-derived displayable `owned` rows. Count `activeSquad` from squad IDs that are in that set. Keep the normal count wording exactly unchanged for normal saves.
2. For squad IDs without a displayable Unit Box profile, append a read-only status count, e.g. `1 active · 1 squad profile unavailable`, while keeping the separate unresolved **roster** count.
3. For an all-unresolved roster, use a truthfully non-selectable detail placeholder instead of asking to select a unit. Preserve the existing empty-save placeholder and filtered-no-results behavior.
4. Do **not** write `P.roster`, `P.squad`, player EXP/evolutions, Zel, Karma, Gems, the v7 storage key, or any other save data. Do not invent recovered unit metadata or silently discard IDs.

No changes to CSS, HTML, Java, Android package/manifest/Gradle, source sprites, player economics, battle logic, summon, quest or user save schema. The existing Unit Box count retains its single polite live region, and the unresolved note stays a non-announcing `role=note`.

## Test and limitations

`test_bf_unit_box_active_counts_v27800.py` registers both a quick source-only gate and a real, disposable Chromium regression against the packaged `index.html` and nav CSS/JS at **320, 359, 393, 540** CSS px. It tests normal six-unit save, one resolved + one unavailable squad ID, filter clear and unchanged state, all-unresolved roster and unavailable detail message, truly empty roster, no page errors or horizontal overflow. All unknown unit IDs exist **only in a throwaway in-memory browser context** with blocked network; no owner's save or Android app is loaded.

The local reproduction using the actual v277 APK-extracted HTML/nav assets plus the same scoped candidate changes **PASS 4/4 viewports**, no synthetic player-state writes or page errors. GitHub exact-head CI still required before promotion; do not claim full CI or signed APK acceptance until it actually finishes.

## Merge and owner safety

This is a new **draft** PR stacked after v277 solely to resolve Claude v271 N1/N2, not a new release, APK install, original 2022 visual parity claim, or permission to bypass the v273 merge block. Do not merge early. Require exact-head six source preflights, full Android signed build, identity/certificate and standard APK hash receipt, browser regression, then retarget to post-v277 merged main and revalidate. Keep owner's installed v265, real v7 save and existing roster/Gems/quest progress untouched. UI estimate ~65%, overall original 2022 game ~30% provisional and unchanged.
