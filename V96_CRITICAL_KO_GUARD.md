# Brave Frontier Global Offline — v96.00 combat correctness

Base: v95.00 verified `d8dc6683b753748a1239e0682be041c4ae38a8aa` (public repo Build #6 SUCCESS).

## Changes
- v95 source-scoped multi-hit normal criticals now evaluate strike contact against **remaining demo target HP** before drawing an individual 10% critical roll.
- Later positive-damage frame entries after an earlier frame has already defeated the enemy are **not treated as landed hits** and cannot generate phantom critical counts or critical UI notices.
- Each source hit trace now includes `landed` and `appliedDamage`; the existing archived damage weights, timeline, full DEMO damage formula, 150% source critical multiplier, and normal battle execution remain unchanged.
- New browser tests cover three landed hits, one-hit early KO (critical and ordinary) and save immutability. Packaged APK asserts the guard and same package/signature arrangement.
- Native overkill, extra hits, spark, enemy defenses and other unverified mechanics are still excluded, **not emulated**.

## Safety
- `org.bravefrontier.offline` unchanged.
- `bf_global_offline_demo_v7` unchanged; no save-format migration.
- CI still requires `BF_DEBUG_KEYSTORE_B64` to build the signed APK.
- No signing material, network request or saved-game fields introduced.
- CI + APK signing do not replace on-device Android gameplay testing.
