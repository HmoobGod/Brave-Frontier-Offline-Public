# v271 — Unit Box saved roster with missing archive profiles

**Source baseline:** merged v270 main `9ea08f2d46413caae09637aa5dbbe84805e140bf`. Source-only/UI-focused follow-up to Claude's v269 nonblocking N5. Preserve the owner's working v265 APK, v7 save and real units/Gems/quests.

## User-visible issue

The offline Unit Box previously filtered `P.roster` through `effectiveUnit(id)`, silently dropping any saved unit ID not present in the recovered offline archive. If every ID was unresolved, the panel incorrectly said **No owned units are available in this offline save**, even though the saved roster was nonempty. This patch does **not** delete, repair, load, invent or mutate any unit.

## Presentation-only fix

- Compute read-only `owned` (resolved archive profiles), `unresolved` (saved IDs whose display profile is absent), and existing `filtered` result arrays from the same in-memory `P.roster`.
- For a mixture, retain all valid unit cards while adding a small noninteractive availability note that counts the unresolved saved IDs and explicitly says the roster was not changed. The note is `role=note`, **not** an additional live region.
- When every saved ID is unresolved, show **Saved units are present, but their archived profiles are unavailable.** Do not offer a useless filter reset.
- When the real roster is truly empty, preserve the existing **No owned units are available in this offline save.** message, card count and no-reset behavior.
- In unresolved cases, label visible records as **resolved** instead of claiming an incomplete archival listing is the full owned roster. The existing separate polite count status includes the number of unresolved IDs.
- Preserve valid-card image handling, filter and sort order, ownership semantics, active squad and unit-detail navigation, archived art, previous accessibility fixes, no-result Clear Filters behavior and focus.

## Validation

Local browser smoke using the **real signed v270 APK's `index.html` and archived navigation JS/CSS** with candidate v271 UI changes passed at widths **320, 359, 393 and 540 pixels** in disposable network-blocked Chromium. Tested normal six-unit state, six valid plus one unresolved saved ID, two unresolved IDs with no available profiles, real empty roster, no-match search and Clear Filters restoration. In every case read-only refreshes and UI interactions left the synthetic roster, squad, unit EXP, evolutions, Gems, Zel, Karma and in-memory `bf_global_offline_demo_v7` storage unchanged. No JS exceptions or new horizontal overflow. Synthetic unknown IDs 999999997/999999998 were injected **only into the isolated browser**, never an owner device or saved file.

The new `test_bf_unit_box_unresolved_v27100.py` repeats the four-width tests in signed Android CI and has a source-only gate. Existing v269 and v270 tests remain registered.

## Exact-head review and merge policy

Changed files should be limited to `bf_home_nav.js`, `bf_home_nav.css`, new v271 read-only test, this document and two workflow registration files. No `index.html`, Java, Android manifest, Gradle, source art, save schema, save writes, gameplay, combat, summon rates, economy, signing or Internet permission change.

**Draft only:** require independent Claude exact-head source/browser APPROVE, all six exact-head PR source preflights, completed signed Android PR merge-tree CI, verified identity/standard signed APK/diagnostic/missing-index artifacts and signer/version/package match before merging. Physical device and original Global screen-parity acceptance remain separate. Do not install any new APK over v265 without an owner-controlled verified backup and on-device acceptance.

UI reconstruction estimate remains ~65%, original complete game ~30%, both provisional and unchanged by this single screen clarification.
