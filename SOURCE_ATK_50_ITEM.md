# Archived single-ally ATK +50% item

Original 2022 item **#20401 強靭薬** is now selectable alongside the existing
#20400 ATK +30% command in experimental archive combat. The default selection,
legacy `.source` profile and two-argument `useAtkItem(actor, target)` API remain
#20400. The optional third argument accepts only the supported numeric item IDs.

The committed v5000 evidence and compressed battle-item catalog both record
#20401 as group 400, ally target type 1, single target area 1, skill type 5,
parameters `0,50,0,0,0,3`, and maximum equipped quantity 10. No source data is
changed. The Japanese name is retained without inventing a canonical translation.

Both strengths share the previous **one temporary DEMO charge per mission**.
The actor pays the existing Guard action and shared turn reservation; only a
living, active, unbuffed recipient is eligible. Existing buffs are never replaced
by this command, including weaker boosts. Party +50% and single +100% commands
retain their existing separate budgets and stronger-effect policies.

The chosen boost reaches the existing `effectivePlayerAtk` function and normal
and offensive BB attack paths. Three-round expiry includes the cast round;
rounding, prototype damage, stock, action timing and non-stacking remain DEMO.
This does not reconstruct native item ownership, recipes, prices, drops or the
original damage formula. No real inventory is granted or consumed.

The four-width regression uses actual prepared HTML, normal and BB attacks,
shared reservations, strict invalid IDs/blocked phases, KO and buff exclusions,
duration, stock/default reset and legacy API behavior. Full synthetic player and
storage state plus the write counter must remain unchanged. Existing single,
party and double-ATK regressions remain required in Android CI. No save schema,
Gem/Imp adjustment, Android code, signing identity or installed APK is changed.
The packaged-item gate also requires byte equality between the APK's module and
the checked-out source, including both archived profiles and the strength selector.

Run `python3 test_bf_source_atk_50_item.py --source-only` for source checks or
omit the flag after normal asset preparation for the Chromium combat regression.
Physical Android, actual owner saves and native gameplay parity are not certified.
