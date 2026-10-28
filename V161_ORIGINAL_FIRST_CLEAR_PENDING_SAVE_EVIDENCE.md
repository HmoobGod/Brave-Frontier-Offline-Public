# v161 — Preserve original 2022 post-upgrade first-clear evidence (no Gem payout)

## Objective and primary evidence
In v160, all **22 currently playable dungeon finales** with exact owner-2022 mission reward `8:0:1:0:0` appear in the saved `_bfGemV160.legacyFinales` after clearing, regardless of whether the clear happened before or after the v160 update. All 29 source finale mission IDs have independent historical 2015 Global evidence of exactly one first-clear Gem, but seven Amdahl finales remain unplayable. This checkpoint preserves the distinction between older saves and newly completed authentic finales, without crediting any real Gems.

## Actual gameplay implementation
Build-time `patch_bf_original_gem_pending_v16100.py` runs **after** v160's existing save-ledger patch. It adds `_bfGemV161Pending:[]` to the **same canonical `bf_global_offline_demo_v7` JSON save**, with `P.version=7` unchanged. The existing live `awardDemoRewards()` function captures previous quest clear count and, only on a first clear of one of the 22 eligible source-approved finale IDs, appends that ID to the new sorted pending list. It does so before the existing `saveProgress()` transaction. No separate storage keys or currency balances are created.

- First clears completed before v161, including imported v124-era owner saves, continue to be captured in legacy history **without** a newly earned pending marker.
- First clears completed after this patch are marked once, even though v160's original legacy list is also updated during `saveProgress()`. Replays never re-add the marker.
- Seven source-only Amdahl finales (404, 414, 424, 434, 444, 454 and 465) and other nonfinal quests cannot be recorded.
- Parser/save validation rejects duplicate, unsorted, unrecognized, missing-clear, oversized or malformed marker entries through existing recovery/quarantine behavior.
- **No Gem rewards, spendable balances, 7★, unverified enemy formations, item purchases, battle damage, or Android signing/package/network behavior are changed.** `_bfGemV160.balance` stays zero and `paidFinales` stays empty.

## Verification
Playwright against the exact prior v160-patched Android `assets/index.html` proves a genuine live `awardDemoRewards()` first clear (#12), replay, another first clear (#23), import of a pre-v161 old save with #33 previously cleared, replay of #33, new clear #43, Amdahl #404 rejection, wrong pending IDs and duplicates, one canonical-key write, simulated quota failure and byte-exact save-parser roundtrip. Offline source checks pin 29 original 2022 finale records and the 22/7 split to v156 SHA256 `0086bcd4f08b1fc6a748c800f5444221afbb1c1a6fc749e9c7e593111498b3c8` and v157 historical explicit Gem counts. A signed APK verification step confirms byte-identical bundled HTML and package/signing/no-INTERNET invariants.

## Remaining limitations
The pending marker is an **editable local record**, NOT original server-side achievement claim proof or an automatically redeemable Gem. A prior APK that doesn't know the field can drop it on save; future currency activation needs a documented downgrade policy, export/backup test, wallet ceiling/accounting and validation of old-account rewards. Issue #80 tracks those requirements.

**Merge gate:** v160 merged-main Build #546 SUCCESS, exact v161 feature-head CI SUCCESS, guarded merge, then new merged-main CI SUCCESS. Installed owner v124 APK/save remain untouched.
