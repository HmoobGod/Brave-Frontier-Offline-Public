# v160 — Production v7 save-compatible original Gem clear-history foundation

## Background and authenticated sources
The owner's original 2022 Global mission master `F_MISSION_MST_1_Ver1118.json` (SHA256 `d4e364b6c1c5a825c0153c57bdd4123cd35800c74db795d913d119b6c9a99f83`) carries the original `8:0:1:0:0` fixed reward on 29 distinct dungeon finales, and the v156 exact prerequisite join identifies **22 playable** versus **7 Amdahl unplayable** finals. Independent 2015 Global archived missions explicitly specify `clear_bonus:[{"gem":"1"}]` on 29/29 corresponding IDs, with eight negative controls. Source v156 canonical SHA256 `0086bcd4f08b1fc6a748c800f5444221afbb1c1a6fc749e9c7e593111498b3c8`.

## Direct inspection of actual signed APK
The signed merged-main **v158 Build #540** artifact was downloaded through the connected GitHub Actions artifact endpoint. Its exact bundled `assets/index.html` is ~8.06MB, SHA256 `8a6e8c7969810cb58da4dcf2809675dff9cb776ebc8b0f4f95117f721355340c`. The current live app code uses `defaultProgress()`, `parseProgress(data)` and `saveProgress()`; `saveProgress()` writes `JSON.stringify(P)` to `bf_global_offline_demo_v7`. `awardDemoRewards()` increases `P.questClears[QUEST.missionId]` on every quest replay. The old save parser drops new unknown fields, so simply attaching a separate wallet loses data after reload.

## Actual production change (no currency yet)
A small, assertive **build-time patch** `patch_bf_original_gem_ledger_v16000.py` runs after existing bundled HTML transformations and before tests. It adds a hidden namespaced `_bfGemV160` object to **the existing** player save:

```json
{"schema":1,"balance":0,"paidFinales":[],"legacyFinales":[]}
```

- **Same save key and save version**: `bf_global_offline_demo_v7` and `P.version=7`. The new field is part of the **same single JSON storage transaction** as quest clears; no second key, service or network.
- On loading old v1–v7 saves without the new field, derives `legacyFinales` strictly from completed 22 source-confirmed playable finale IDs. 7 Amdahl source-only finales cannot appear in that ledger. All existing quest/squad/roster/resources are parsed by the previous code unchanged.
- When a new finale is completed while v160 is installed, `saveProgress()` updates `legacyFinales` from the current quest clears before making its existing **single** storage write. It does **not** grant or withhold any actual gems, convert demo currency, or change the quest's DEMO completion rewards. The legacy history is an audit foundation, not irreversible proof of a native claim.
- The `balance` field must remain **zero** and `paidFinales` **empty** for v160. Any save claiming a positive Gem wallet or malformed ledger is rejected by `parseProgress`, which triggers the game's existing **non-destructive save quarantine/recovery** instead of overwriting saved progress.
- Existing 72 forms, 106 playable story quests, original mechanics/QoL, Android identity/signing, offline no-INTERNET, default game assets and owner installed v124 remain unchanged. This does not promote Amdahl, 7★ or source-only skills.

## Verification
The pre-production patch was applied to the **actual v158 signed APK HTML** extracted locally, then launched in Playwright. Tests demonstrated: old v7 saves missing `_bfGemV160` migrated conservatively; original roster/squad/materials/unit EXP and other fields preserved; a new finale updates the same canonical key, not another wallet; replay does not create rewards; manual save/reload exact roundtrip; corrupt/fabricated wallet and claim values fail closed; a simulated storage quota failure preserves the previously persisted save. The same tests are registered in GitHub CI plus byte-for-byte signed APK test.

## Important restrictions
1. **No live Gems are earnable or spendable yet.** Both historical `balance` and `paidFinales` remain zero/empty. Native 2022 payout, reimbursement rules, exact Gem cap, and old-account claim semantics are not proven.
2. A **downgrade to an older APK** can parse most v160 saves but will drop the namespaced field on the next old-version save; the field's *legacy* contents are fully recoverable from the original `questClears` while payouts remain disabled. Future nonzero Gem wallets must not allow this downgrade without backup/export warnings.
3. Source-evidenced 22 playable finales are not a license to award retroactive Gem balances without deciding account migration. Owner save remains protected.
4. This is a **real production save-schema extension** without increasing `P.version`, not a user-visible Gem feature. Never advertise spendable Gems based on v160.

## Integration process
Require exact v160 feature-head GitHub Actions green and v159 merged-main Build #544 green before merging. Then require new merged-main CI and, before first live reward activation, verify an update on the owner's v124 device/save backup. The source and implementation are tracked under Issue #80.
