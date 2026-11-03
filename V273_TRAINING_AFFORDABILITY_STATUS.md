# v273 — Demo Training affordability status (read-only UI)

**Upstream dependency:** v272 PR #207 current exact source head `9bcbde4f0e7409164bbab4790d8299e9095c79cf`. v272 itself is stacked on v271 PR #206 head `1c86beae8913053df86c8286b8e957e328d8e6ae`, while merged main remains v270 `9ea08f2d46413caae09637aa5dbbe84805e140bf`.

This PR is **not independently mergeable** until v271 is independently Claude-approved, signed-CI checked and merged; v272 is then rebased and re-reviewed, signed-CI checked and merged; v273 is rebased onto resulting main, then independently reviewed at its new exact head with fresh signed CI. No inherited CI or review approval is sufficient after the head moves. The owner's actual v265 APK and v7 saves remain untouched.

## User-facing problem

The reconstructed UI has a Demo Training area showing Shards, Zel and a per-unit Train button. The explanation says +10 EXP costs 1 Training Shard and 150 Zel; +50 EXP costs 5 Shards and 750 Zel. However, users cannot tell from the current toolbar when neither, only the smaller, or both actions are **resource-affordable**, especially when training has hit the 100,000-Shard lifetime spending cap. The original 2022 Brave Frontier **Fusion** is not reconstructed; do not imply this is recovered native Fusion behavior.

## Change

After the existing `#trainingbalance` toolbar element, add a single read-only, full-width, accessible polite status message. It derives affordability only from the already-present in-memory `P.trainingShards`, `P.zel` and `P.trainingSpent`. It tells the user whether available resources support either demo enhancement tier, what minimum currency is missing, or whether the spending cap is reached. Messages expressly qualify that each unit must also pass its unchanged level and EXP limits. The existing `renderTrainingPanel` balance text mutation triggers a `MutationObserver` to refresh the message; reselecting Training also refreshes it. The status element is inserted once, uses `textContent`, and never changes `P`, saved data or unit eligibility.

The new CSS arranges the note as a full-width wrap item within the existing Training toolbar, with a readable contrast and no new hidden/display rules. There are no changes to `index.html`, the original training functions, thresholds, spend/refund, Quest awards, Training Shard generation, save schema, Gem/Zel economy, original source art, Android identity, manifest, Gradle or signing.

## Source and browser evidence

An isolated local run using the **real v272 signed APK's packaged HTML**, prepared artwork and source navigation code plus this v273 UI candidate passed all **four** viewport widths (320/359/393/540 px), across **nine resource states** each, checking missing Shards, missing Zel, both missing, +10-only affordability, +10/+50 affordability, near-cap restrictions and 100,000 spent cap. All 36 resource cases passed. Test confirmed a single status node with `role=status`, polite atomic announcements, updates on Training tab reentry, no extra overflow, no browser errors and **no synthetic player/save changes** after the display refresh. All storage was private in-memory browser data; not the owner's APK or game progress.

`test_bf_training_affordability_v27300.py` repeats these checks in signed Android CI, after packaged HTML art preparation. Source-only CI checks module budgets, absence of Internet permission, source registration, and no forbidden CSS display override. Exact-head CI is still required. The v272 screenshot receipts will also capture the updated Training UI as source-browser evidence, but **not** original 2022 visual parity or phone/TalkBack acceptance.

## Review and merge gates

Expected changed files: `app/src/main/assets/bf_home_nav.js`, `bf_home_nav.css`, new v273 regression test, this document and two CI workflow files. Do not install, uninstall, clear, export, restore or otherwise modify the owner's working signed v265 APK or actual v7 saves. Keep the PR **DRAFT** while upstream v271 and v272 remain unmerged. Require all six exact-head source preflights, complete full signed Android Build with all four APK/identity/fault/diagnostic evidence groups, independent Claude exact-head source/browser approval, and rebase onto the new approved main before final v273 merge.

This is a small UI clarity improvement, not recovery of original game systems. Estimated UI reconstruction ~65% and full original 2022 game ~30%, both provisional and unchanged.
