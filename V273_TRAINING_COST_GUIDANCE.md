# v273 — Current Training affordability status (UI only)

## Stack and source of truth

v273 is a draft on v272 PR #207 (source head `9bcbde4f0e7409164bbab4790d8299e9095c79cf`), which depends on v271 PR #206 (`1c86beae8913053df86c8286b8e957e328d8e6ae`). Merged main remains v270 `9ea08f2d46413caae09637aa5dbbe84805e140bf` at development start. **Do not merge out of order.** After v271 merges, retarget/rebase v272 and review it at the new head; after v272 merges, retarget/rebase v273 and rerun CI plus Claude review.

## Problem

The packaged `index.html` already describes the demo Training Shard and Zel costs in its intro. An initial v273 static cost note duplicated that description; the full-screen local render exposed this and the candidate was corrected **before PR creation**. The remaining useful information is the current resource affordance: the disabled +10 EXP / +50 EXP ×5 controls give no concise live explanation of which action the balance supports.

The existing game grants 10 EXP for 1 Training Shard + 150 Zel, and 50 EXP for 5 Shards + 750 Zel, subject to busy state, unit eligibility, demo spending caps and EXP caps. This is demonstration training, **not** original 2022 Brave Frontier Fusion.

## Final runtime change

Add one read-only, noninteractive `role=status`, `aria-live=polite`, `aria-atomic=true` affordability message immediately beneath `#trainingbalance` in the existing `.training-toolbar`. The message is based on the actual in-memory `P.trainingShards`, `P.zel` and `P.trainingSpent` values, distinguishing:

- Insufficient resources for +10 EXP: states which minimum Shards and/or Zel are lacking.
- Balance supporting only +10 EXP: explains that +50 EXP ×5 needs 5 Shards, 750 Zel and adequate demo spending capacity.
- Balance supporting both actions: explicitly says unit level, EXP and battle restrictions still apply.
- Reached demo training spending limit: warns training is capped.

A one-way `MutationObserver` on the original `#trainingbalance` text refreshes the message after existing balance render updates. Reentering the Training tab refreshes it too. The observer never watches its own note, never writes `P` or `localStorage`, and does not click a training action. Updating text only when changed avoids needless repeated announcements. Styles use 12px wrapped text within the responsive toolbar. All original training functions, resource changes, disabled buttons and save logic remain untouched.

## Tests and safety

Local offline, disposable Chromium tested the *actual signed v272 APK packaged HTML* with the candidate navigation JS/CSS at **320, 359, 393 and 540 CSS px**: **4/4 PASS**. Covered initial zero-shard/zero-Zel unavailable message, 1 shard + 150 Zel supporting only +10, 5 shards + 750 Zel supporting both, and restoration of the synthetic zero balance. Verified exactly one polite status, font 12px, no extra viewport overflow or JavaScript errors, existing training buttons disabled when resources are zero, and no mutation of synthetic roster, squad, Training Shards/Used, EXP, evolutions, Gems, Zel, Karma or in-memory v7 localStorage after returning to initial values. Simulated balance changes were in throwaway browser memory only; no owner data was loaded.

Expected six-file scope vs v272: `bf_home_nav.js`, `bf_home_nav.css`, new `test_bf_training_cost_guidance_v27300.py`, this document and two CI workflow registrations. No `index.html`, game logic, input costs, server/archive data, saves, original art, Java, manifest, Gradle, signer or Internet permission changes.

## Required review gates

PR stays **DRAFT**. Require v271 independent exact-head Claude APPROVE, signed APK identity and merge first; v272 then rebase/retarget, full exact-head CI/identity/screenshot artifact verification, Claude approval and merge. Finally rebase/retarget v273 to merged main and require all six source checks, complete signed Android CI (legacy Unit Box/quest/save regressions), signed identity/diagnostic/missing-index APKs, and new independent exact-head Claude APPROVE before merge. Owner installed v265 and actual v7 save, units, quests and Gems must remain untouched. Screen-reader TalkBack, physical Android appearance and original 2022 pixel parity remain untested.

UI reconstruction ~65%; full game ~30%, both provisional, unchanged.
