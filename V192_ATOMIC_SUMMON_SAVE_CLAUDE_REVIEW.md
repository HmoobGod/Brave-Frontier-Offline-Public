# v192 — Atomic save for existing offline demo token summons

**Status: draft feature; not merged or owner-tested.**

## Problem found in owner-tested v188 source

The current offline demo `E.summonbutton.onclick` handler reduces
`P.summonTokens`, adds a recruit to `P.roster`, and appends to
`P.summonHistory` **before** calling `saveProgress()`. It does not check
the result. On full/blocked local storage, save recovery pending, or parser
validation failure, the action can display a recruited unit that was not
persisted. This is separate from original BF Global summon probabilities
and from Personal Offline Gems.

A second defensive limit exists: `parseProgress` rejects
`summonHistory.length > 100`, but the old event handler unconditionally
pushes. The new handler bounds that existing save field.

## Change

A narrow build-time patch, `patch_bf_atomic_demo_summon_v19200.py`,
runs after the existing v173 Gem claim patch and changes only the existing
demo-token recruit handler and button disable condition in the prepared HTML.

The action still costs **exactly one existing demo summon token**, picks
uniformly from only the currently unowned **existing demo recruit pool**,
and never invents native 2022 summon rates or new playable units. No personal
Gem amount, claim, reward, mode, original Gem wallet or summon-token
earning rate changes.

Transaction:
1. Check existing battle state, canonical v7 version, token/remaining
   recruit requirements and `saveRecoveryPending` before RNG and mutation.
2. Copy the full **current canonical P** (not just token count) because the
   existing `saveProgress` validator may normalize stored optional wallets.
3. Apply the old one-token cost and recruit, cap history at **last 100**
   original recruit IDs.
4. Attempt **the same single canonical `saveProgress()` write**.
5. On failure, restore all of P immediately and show a failure message
   explicitly confirming that no token or recruit was retained.
6. On success, show the usual recruit result and refresh the existing
   unit/summon UI.

No new save field, storage key, network access, Android permission, package
ID or signing rule is added. `bf_global_offline_demo_v7` remains the save
key and `P.version=7`.

## Verification

- `test_bf_atomic_demo_summon_v19200.py`: full prepared HTML at 390×844
  in Chromium; real summon click with deterministic RNG; simulated storage
  failure and complete in-memory + persisted state rollback; valid save
  commits exactly one recruit and token; parseProgress roundtrip; no duplicate
  with zero tokens; 100-entry history limit; blocked save-recovery action;
  untouched original and personal Gem schemas.
- `test_bf_packaged_atomic_demo_summon_v19200.py`: inspect the **actual
  Gradle APK** for exact prepared HTML bytes and the atomic handler,
  untouched original v7 key, existing v170/v173 Gems and prior v191 source
  assets. This is not an Android WebView execution test.
- All previously registered GitHub Actions regressions stay in the workflow,
  including v188–v191 features, original rewards and save migration tests.

## Known limits / release gates

- An in-memory rollback cannot roll back an already-persisted user save
  written by an unusual storage implementation that reports a false negative
  after committing. Standard localStorage writes either complete or throw.
- This improves **existing demo-token summons only**. It **does not implement
  Personal Offline Gem spending**, which is separately tracked in issue #120,
  and it does not restore original 2022 summon mechanisms.
- Before merging: v191 merged-main Build #865 on
  `f8e655f9f7837adeeb051b0bd7e896acaf18727e` must be green,
  v192 exact-head feature CI must pass, and **independent Claude review is
  required** because real saves/rosters are involved. Then use SHA-guarded
  merge and fresh green merged-main CI.
- Owner's installed v188 remains the owner-tested baseline. When upgrading,
  ensure existing v124→v188 save, Gems, Imp inventory, quests, training,
  battles and new summons survive without uninstalling.
