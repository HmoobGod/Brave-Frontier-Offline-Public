# v273 — Explain actual demo Training Shard and Zel costs

## Dependency / source baseline

This patch is stacked on **v272 PR #207** at source head `9bcbde4f0e7409164bbab4790d8299e9095c79cf`, which itself depends on **v271 PR #206** at head `1c86beae8913053df86c8286b8e957e328d8e6ae`. Authoritative merged main at development start remains v270 `9ea08f2d46413caae09637aa5dbbe84805e140bf`. All future mergers must respect v271 → v272 → v273 ordering; after upstream merges, rebase/retarget onto the actual merged main and get fresh exact-head CI and Claude approval for every affected PR.

## Problem and evidence

In source-browser screenshots, the Training screen shows disabled **+10 EXP** and **+50 EXP ×5** controls with a header reporting shard balance, but the actual requirements are available only through disabled buttons' `title` attributes, not clear visible explanatory text. That is particularly ambiguous on touchscreens.

The packaged game’s existing `index.html` training code says a 1x action spends **1 demo Training Shard + 150 Zel** and grants **10 EXP**; a 5x action spends **5 Shards + 750 Zel** and grants **50 EXP**. The original controls also enforce busy state, unit level and various budget/cap limits. This is *not* original Global Fusion.

## Change

Add one short, noninteractive `role=note` paragraph immediately after the existing `.training-toolbar` when the navigation shell initializes. It states the two existing costs and notes that unit level/spending limits apply. Guard against duplicate insertion. Use `textContent`, not HTML injection; style the note at 12px with wrapping and a muted border. No live region, new button, reward, interactive cost calculation or access to save state.

This patch intentionally **does not change the existing `index.html` training logic**, resource balances, unit EXP, roster, evolution, affordability, button disabled logic or progress. It does not claim original 2022 Global economy.

## Tests and limitations

A local source-browser test using the *actual signed v272 APK's* packaged `index.html` and nav JS/CSS plus the candidate v273 presentation-only edits passed at **320, 359, 393 and 540 CSS px**. Verified exactly one visible `role=note`, the accurate cost pairs, 12px readable text, disabled demo Training buttons with zero starting resources, no extra horizontal overflow, no JavaScript exceptions, and no changes to synthetic roster, squad, Training Shards, Training spent, unit EXP, evolutions, Gems, Zel, Karma or in-memory `bf_global_offline_demo_v7` storage after navigation. Real owner save was never accessed. `test_bf_training_cost_guidance_v27300.py` registers the same source and full-browser assertions in CI.

Expected six-file diff relative to v272: `bf_home_nav.js`, `bf_home_nav.css`, new `test_bf_training_cost_guidance_v27300.py`, this document and two CI workflow registrations. No `index.html`, Java, Gradle, manifest, signer, package identity, original artwork, archive records, gameplay, costs, caps, reward logic, training shards, saves, or network permission changes.

**Acceptance gates:** keep PR draft until v271 independently approved/merged, then v272 rebased/retargeted, exact-head reviewed and merged, then v273 rebased/retargeted. At each final head require 6/6 source preflights, completed signed Android build including legacy game/save/Unit Box tests, standard signed APK, v251 identity certificate/version/head match and distinct diagnostic/fault APK artifacts, followed by fresh independent Claude approval before marking ready/merging. On-phone display/assistive technology and original 2022 visual parity remain untested. Never install, clear, or alter user's working v265 device or v7 save.

Estimates remain **UI ~65%**, whole original 2022 game **~30%** provisional; a small accessibility/presentation improvement does not justify increasing either.
