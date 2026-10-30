# v198 — Opt-in PERSONAL OFFLINE Gem summons (review candidate)

**Merged v198 (PR #127):** Claude reviewed exact commit `c30277ad` and approved with conditions; merged as `e40924d7`. Android device verification remains pending. v198.02 hardening is separate and requires new CI and Claude delta review before merging.
This is a player-requested custom offline economy feature, **not** a recovered
2022 Global summon price, rate table, roster, banner, or Gem spending rule.

## Behavior

- The existing *PERSONAL OFFLINE* wallet (v170) can buy a unique unowned
  **existing DEMO recruit** for **100 custom Gems**. Original mode is not
  eligible; it remains unchanged. No new unit forms, genuine banner rates,
  recruitment pools or original 2022 Gem debits are introduced.
- The original one-**DEMO token** summon button (v192) and its uniform
  unowned-recruit selection remain in place. The new button is separate.
- The original source-based 1-Gem dungeon first-clear ledger (v173) is not
  debited. Welcome/daily/quest/replay personal earnings remain unchanged.

## Save migration and transaction

- Existing storage remains **only** `bf_global_offline_demo_v7` with
  `P.version=7`. New and older non-purchasing personal wallets remain
  `schema:1`; a real successful purchase converts **only the optional**
  `_bfGemV170Custom` wallet to `schema:2`.
- A schema-2 wallet adds `spent` and strictly shaped
  `receipts:[{unitId,cost}]`. All receipt IDs must be distinct, present in the
  saved roster and in the existing valid demo recruit pool. Every receipt
  costs exactly 100 personal Gems. `spent=100×receiptCount`; the legacy
  v170 validator still verifies **all earned** Gems by using
  `earned=balance+spent`. Invalid, forged, incomplete, duplicated,
  overdrawn, unexpectedly shaped or wallet-overflowed records are rejected.
- The purchase validates mode, save recovery, funds and eligibility before
  the random selection. It copies all canonical P state, then applies
  one 100-Gem debit, unique demo roster addition, capped summon history and
  receipt in **one existing** `saveProgress()` write. A rejected/quota save
  restores the complete pre-purchase P and displays a failure message.
- After conversion, v170's existing daily claims and quest rewards keep
  working because their strict earned-balance reconciliation now includes
  the supported receipt ledger.
- No new storage key, Android permission, package ID, signing key or
  internet dependency. The signing and save format remain the same.
- **Downgrade caution:** older APKs cannot interpret schema-2 wallets.
  Export a full v7 backup before installing an older APK; don't downgrade
  and play/save over new purchases.

## Tests and gates

- `test_bf_personal_gem_summon_v19800.py` covers actual Chromium purchase
  button, schema-1 compatibility, first schema-2 purchase, exact 100-Gem
  charge, unique recruits, no demo token spent, persisted parse roundtrip,
  Original-mode refusal, receipt corruption rejection, subsequent daily
  rewards, storage quota failure rollback and no new storage keys.
- `test_bf_packaged_personal_gem_summon_v19800.py` independently inspects
  the compiled Android APK and canonical HTML/UI, unchanged v192 token
  action, separate original v173 ledger and APK identity.
- Existing v170/171/173/192 original / personal Gem, Imp, downgrade, save
  recovery, APK and combat tests stay in the GitHub workflow.
- **Must get Claude's independent approval on exact head**, especially the
  optional schema migration and interaction with existing v7 imports,
  backup rotation, v173 original claims and v171 Imp save normalization.
- Then exact-head green CI, SHA-guarded merge, fresh merged-main green CI;
  owner's Android in-place upgrade and real save tests remain separate.

**Scope boundary:** This feature does not solve native 2022 enemy-wave
formations/AI or original EXP progression. The existing 106-quest demo
combat and source-only 36 Amdahl quests are unchanged.

## v198.02 Claude review follow-up — persistent receipt eligibility

- **Future developer invariant:** Every unit ID already recorded in any
  schema-2 `receipts` array must remain eligible under `RECRUIT_IDS` **and**
  remain valid in the canonical roster across future data updates. Never
  rename, recycle, remove or reassign purchased recruit IDs without a
  tested, compatible save migration. The existing `summonHistory` validator
  has related ID-stability requirements. The v200 regression now pins the 12 original v198 DEMO recruit IDs from the exact merged-v198 source blob in `source_data/bf_v198_recruit_id_compat_baseline_v200.json` and tests a constructed (not owner-exported) two-receipt schema-2 save. The CI gate detects future removals/renumbering/reclassification of those historical IDs; genuinely owner-exported schema-2 save bytes and actual Android device compatibility remain unverified. Require a reviewed migration for any deliberate ID change.
- `BFGlobalCustomGemsV17000.snapshot()` must return a detached frozen
  receipts array containing detached frozen receipt objects, not references
  to the live canonical wallet. The schema-1 snapshot keeps its prior keys.
- The v170-v198 economy receipts are **consistency checks**, not anti-cheat.
  Manual editing of an offline player's JSON is not cryptographically
  prevented.
- Local Android Studio / Windows builds are not interchangeable with
  GitHub Actions APKs; see `BUILD_APK_PC_GUIDE.txt`. A direct Gradle build
  missing the runtime Gem patch chain is a destructive downgrade risk after
  any schema-2 purchase.
- Owner Android upgrade, in-app purchase, first-clear/replay, import/export,
  Imp actions, original claims, and persistence still need device testing.
