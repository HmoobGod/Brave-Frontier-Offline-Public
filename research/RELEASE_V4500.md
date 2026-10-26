# Brave Frontier Global v45.00 — Shared DEMO Battle Item Action Reservation

Baseline: successful v44.00 Build #253, commit `ade1c49943af3f9dafa64baef7dc887fbf41a8ab`.

## Repaired loophole

The v42 Potion, v43 party heal and v44 +30% ATK prototypes each tracked their own actor usage. A user could clear or re-queue the actor's Guard and use a different temporary item using the same actor during the same DEMO round, obtaining two item effects with only one Guard action paid. v45 introduces an ephemeral shared actor reservation: **at most one of these three temporary item types per active actor per round**. The action is reserved before the effect is granted, and the original per-item quotas and action enforcement remain. The ledger automatically clears on a new battle state or subsequent round; no save data or inventory is touched.

The shared reservation is **DEMO consistency logic, not verified original Brave Frontier item mechanics**. Source-backed v43 item #20100 still identifies a party-targeted item, but its healing quantity remains simulated (+250). Source-backed v44 item #20400 continues +30% ATK for three DEMO rounds on one ally. Native action timing, item consumption, stacking, effects, and inventory behavior remain unverified and are not claimed restored. All existing art, dialogue, quests and old tests remain in place.

## Verification

CI adds Chromium cross-item double-spend/guard/restart/round-reset/save-isolation checks and APK packaging/identity checks. Inherited v42-v44 tests are retained and remain valid without the optional new module. Keep Java load order v41 -> v45 lock -> v42 Potion -> v43 group heal -> v44 ATK. Package `org.bravefrontier.offline`, original stable development debug signer, no INTERNET, and `bf_global_offline_demo_v7` are unchanged.

Physical-device installation, Android WebView rendering and real-device save durability are NOT asserted by CI.
