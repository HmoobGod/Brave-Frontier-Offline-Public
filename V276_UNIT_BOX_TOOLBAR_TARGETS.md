# v276 — Unit Box toolbar 44px mobile targets

## Dependency
This is a narrow UI-only patch stacked on **v275 PR #212** at exact source head `327a11b20efd65db15552783afe80a967b29cf40`. The canonical unmerged review chain is v271 #206 → v272 #207 → v273 #208 → v274 #209 → v275 #212 → **v276**. Merged main remains v270 at `9ea08f2d46413caae09637aa5dbbe84805e140bf`. No PR in this chain may bypass an earlier review, merge, rebase or exact-head CI gate.

## Problem and limited change
The existing Unit Box search/Show/Element/Rarity/Sort controls have CSS min-height **37px**, below the 44px mobile touch target used for Training in v275. The existing Unit Box keyboard focus outline already has a 3px outline and should be reused, not replaced. The v276 CSS uses a `body.bf-menu-mode .bf-owned-box` selector to lift input/select min-height to **44px** without touching form values, filter logic, labels, sort order, Unit Box cards, owner roster or saved state.

## Verification
`test_bf_unit_box_toolbar_targets_v27600.py --source-only` asserts scoped CSS, inherited visible focus, workflow registration, no Internet permission and navigation JS/CSS byte budgets. The full browser test renders the actual packaged `index.html` and current navigation JS/CSS in isolated network-blocked Chromium at widths **320/359/393/540px** with in-memory localStorage. It checks five controls' width/height, 3px solid focus styling, safe filter/reset behavior, six default cards, no extra page overflow/errors and unchanged synthetic roster/squad/unitExp/evolutions/Gems/Zel/Karma/v7 storage. It does not click real gameplay/reward controls or access the owner's phone.

## Scope and promotion
Exactly five files vs v275: this note, a new regression test, CSS-only scoped Unit Box sizing, and two CI workflow registrations. No changes to JS, HTML, original sprites, Android/manifest/Gradle/signing, network, squad selection, quests, battle, recruits, Training, Gems, Zel, roster or save schema. The measure is reconstructed UI usability, **not** original 2022 Global visual acceptance. Keep DRAFT until v271–v275 independently review/merge in order, v276 is rebased onto final merged main and six exact-head source preflights/full signed Android build+identity pass, then receive Claude independent final-head approval. Do not install/clear/reset the owner's working v265 or real v7 save. UI ~65%, original full game ~30%, provisional and unchanged.
