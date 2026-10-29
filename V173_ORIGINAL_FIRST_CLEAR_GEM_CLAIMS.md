# v173 — Manual claims for source-corroborated original dungeon first-clear Gems

## Source and scope

The owner's original 2022 Global `F_MISSION_MST_1_Ver1118.json` has the exact fixed reward payload `8:0:1:0:0` for 29 dungeon finale missions (v155/v156). Independent Global 2015 mission snapshots name `clear_bonus:[{"gem":"1"}]` on all corresponding 29 finales (v157). Only **22 finale IDs** are currently playable; seven Amdahl finales remain source-only.

This increment adds an **offline manual claim** for **one original Gem per authenticated first-clear**, using the existing v161 post-upgrade pending-first-clear evidence. It does not assert the exact original 2022 server delivery flow, invent a wider reward table, or implement Gem-spending summons.

## Save and claim rules

- Continue using `P.version=7`, `bf_global_offline_demo_v7`, `_bfGemV160` (schema 1), and `_bfGemV161Pending`. No separate storage key or new account identity.
- The existing original wallet's `paidFinales` and `balance` fields now permit **zero to 22** source-backed claims instead of zero only. Balance equals the exact count of paid IDs (there is no spending yet).
- A paid ID must appear in the saved **v161 pending list** and the actual saved quest-clear history. It may **not** appear in the v170 Personal Offline wallet's `firstPaid` list. This prevents double first-clear payment when someone used the custom 100-Gem finale rewards.
- Already-cleared older v124 quests become **legacy history only**, with no retroactive original claim eligibility. Replays do not create new original pending events.
- To redeem newly eligible original finale Gems, switch to **Original** mode and use the dedicated claim button. Claims are explicit and not automatically granted on entry or every quest replay.
- On a failed canonical save, the new original wallet change is rolled back in memory and the previous serialized v7 save is unchanged. A user may retry the claim directly after storage becomes writable again; an unrelated game save is not required.
- Strict parser rejects duplicated, unsorted, unknown, unearned, unbacked, custom-first-paid, incorrect-balance and Amdahl IDs. Other saved fields remain unchanged.

## Authenticity boundaries

The two archival snapshots support **one Gem on a dungeon finale first clear**, but the original 2022 claim interaction, max wallet capacity, spending transactions, native summon rates, true original drops, and prior-owner reimbursement rules remain unverified. Therefore the claim workflow is clearly described as offline reconstruction, and no original Gem spending is implemented.

Users should **export their current canonical v7 save before any APK downgrade**. v160–v172 reject saves with positive original Gem balances; older v124-style parsers can discard Gem-claim metadata on their next save. Restore a backup made before downgrading to recover claims. No downgrade is performed automatically.

## Verification gates

- New Chromium test `test_bf_original_gem_claims_v17300.py`: actual quest first clears; source-only claim; no auto-credit; replay protection; custom wallet exclusion; v124 legacy migration; corrupt-claim quarantine; save-quota rollback and retry; same v7 storage key.
- New signed-APK test checks byte-exact patched HTML, original v160/v161/v170 evidence, intact Imp extension, package/signing identity and no INTERNET permission.
- Existing full regression gates remain in Actions. In addition, v172 packaged-version assertion is broadened for newer versions.
- Require **exact feature-head SUCCESS**, guarded merge into the previously verified v172 main, then a new merged-main signed APK **SUCCESS**. Independent Claude review is recommended for the save-validator relaxation and cross-wallet exclusion before merging.

Owner-installed Android v124 and the real owner save are not touched. No Android-device verification is claimed.
