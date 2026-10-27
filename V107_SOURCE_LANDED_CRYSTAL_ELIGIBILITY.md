# Brave Frontier Global Offline — v107 Source-Verified Landed-Hit Crystal Eligibility

Parent: v106 source and save hardening.

## Exact original source inputs
- \`bf8400_original_normal_crystal_checks.js\`: 2,258 source-validated 2022 F_UNIT normal attack hit counts and \`dropCheckCount\` per hit, strict source exclusions.
- \`bf9300_single_hit_critical_combat.js\`: actual source-eligible, positively damaging DEMO single-hit normal attack events.
- \`bf9500_multihit_critical_combat.js\` (v96 post-KO guard): positively damaging *landed* original-timeline normal hits, with post-KO strikes explicitly marked \`landed:false\`.

## v107 result
- For each validated observed normal attack, count exactly \`landed hits × original drop checks per hit\` as **eligible BC checks**, and \`landed hits\` as **eligible HC checks**.
- Exclude post-KO unlanded DEMO strikes from the **confirmed landed-only baseline**, without claiming whether native BF overkill would create additional checks or different rates.
- Strictly reject unrecognized/malformed source profiles, inconsistent struck-damage rows, unconfirmed single-hit events, unknown BB/SBB, simulated enemy events, and other uncertain states.
- Add an optional read-only in-battle audit panel so players and future developers can see the source-qualified *potential checks* next to the older **uncollected reference ledger**.
- No new drops, BC/HC recipients, HP restoration, BB charging, RNG, overkill multipliers, rewards, Energy, battle turns or saved fields.
- The panel only describes up to eight most recent events from each source, **not** a cumulative whole-battle collection tally. It does not assume 2014 data equals 2022.
- The previous v88 normal-event ledger can still roll over all source-listed hits; v107 explicitly warns against treating that legacy reference as actual collected BC/HC.

## Verification
New focused Playwright regression covers real v84 source catalog, 1/3 multi-hit KO boundaries, one-hit original drop checks, bad critical data, source-excluded IDs, 7-field save format and idempotent UI injection. New signed-APK identity/asset checks.
Device test remains separate. Original pickup behavior requires verified recipient selection, HP/BB conversion, overkill and enemy-resistance evidence (GitHub issue #9).
