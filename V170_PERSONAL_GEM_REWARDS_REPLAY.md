# v170 — Personal Offline Gem Rewards (user-approved)

## Owner-selected rates

| Event | Gem reward | Repeatable? |
|---|---:|---|
| First welcome claim after opting in | 1,000 | Once |
| Daily local-calendar-day claim | 100 | Once per day |
| First clear of a regular playable dungeon quest | 25 | Once per quest |
| First clear of a source-verified dungeon finale | 100 **total**, not plus 25 | Once per finale |
| Successful replay of **any previously cleared playable dungeon quest** | 1 | Every completed run |

All 106 currently implemented playable source-verified 2022 Global mission IDs are eligible for custom personal rewards, including 22 original finale first clears. The other seven archived Amdahl finales remain unplayable. At 106 first clears plus 30 daily claims and the welcome gift, this mode earns **8,300 Gems**; replays contribute one additional Gem each. Original 2022 reward references and the original-first-clear evidence remain separate and unmodified.

## Implementation and compatibility

- Explicit **PERSONAL OFFLINE** mode; original mode remains the default with no custom Gem grants. Mode switching preserves a previously accumulated custom balance.
- A v170 custom wallet (`_bfGemV170Custom`) is added to the existing `P.version=7`, `bf_global_offline_demo_v7` JSON save. The wallet and quest clear counter commit through a **single existing localStorage write**; no new account/network endpoint, Gem sidecar, or save key.
- Old v124/v169 saves lacking this optional field migrate conservatively: previously cleared quests enter `legacyClears`; they do **not** retroactively receive the 25/100 first-clear bonuses. A subsequent successful clear of the same quest qualifies as one **replay**, giving **1 Gem**.
- The source-authenticated v160 historical ledger and v161 pending marker remain unchanged (2022 original Gem balance still zero). The custom wallet is a distinct feature and must not be misconstrued as verified original 2022 currency.
- Wallet validator checks exact schema, quest ownership in 106 source mission IDs, sorted disjoint first/legacy claims, and recomputed balance from claim counts. Corrupt/oversized state fails closed using existing save recovery. This is local offline data, not an anti-cheat system.
- Welcome and daily claims are user-triggered and never automatically awarded on an app launch. Dates use **the device's local calendar date**; a second claim on or before the previous claimed date is blocked. Date manipulation on an offline device remains possible; no online authoritative time source is introduced.
- The 1 Gem replay reward is applied in the existing real quest completion function after the quest-clear count increments and before its existing save; no rewards for viewing source entries, an uncompleted run, a lab-only battle, or unplayable archived missions.
- The personal balance can be earned and viewed; **native Gem-spending summons are not yet implemented**. Do not call these Gems usable for a native summon until a separate expenditure path and reversal tests are developed.
- Original equipment/leader skills, unit behavior, Imp progress, training and reward currencies remain untouched. The installed owner v124 APK/save is not upgraded without request. Old APKs may drop unknown Gem metadata on downgrade: **export a complete backup before downgrading**.

## Tests and merge gate

`test_bf_personal_gem_rewards_v17000.py` exercises real Chromium quest rewards including first and repeat clears, original mode, welcome/daily claims, one real canonical save, old v124 migration, Amdahl exclusion, corrupted wallet rejection, storage write rollback, original source evidence, and no extra storage keys.

`test_bf_packaged_personal_gem_rewards_v17000.py` validates the signed APK contains exact v170 HTML/UI, original v160/v161 ledgers, unchanged package/signing identity, and zero INTERNET permissions. v169 Imp package version assertions allow this newer APK label.

Merge only after exact feature SHA CI **SUCCESS** and existing v169 merged-main Build #619 success, SHA-guarded PR merge, followed by a fresh merged-main Android signed APK CI **SUCCESS**. Gems remain opt-in personal mode and independent of Original Global mechanics.
