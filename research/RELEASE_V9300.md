# Brave Frontier Global v93.00 — Original Base Critical Hits on Source-Verified Single-Hit Attacks

**Verified parent:** v92.00 Build #341, commit `1d431bf289b91a486ee3b7720db147afc4e2c4e7`, successful signed Android APK artifact `12597912313`.

## Gameplay integration
Brave Frontier's original base critical hit chance is **10%**, with **150%** critical damage on a successful hit, without additional buffs or resistance. Sources:
- https://bravefrontiereurope.fandom.com/wiki/Gameplay%3ABuffs%2C_Debuffs_and_Status_Ailments
- https://bravefrontierglobal.fandom.com/wiki/Critical_Damage_Boost
- https://bravefrontierglobal.fandom.com/wiki/Damage

The original 2022 Global `F_UNIT_MST_1/2_Ver1084.json` supplies exact normal-hit counts for 2,258 source-validated units, already verified and packaged by v84. New `bf9300_single_hit_critical_combat.js` wraps the existing DEMO player-attack damage calculation and rolls the documented base 10% chance only if this exact unit has **one source-recorded normal hit** and the attack targets an existing living enemy in archive quest mode. When successful, its **one existing DEMO attack damage calculation** is multiplied by 1.5 (integer floored). That makes base criticals a real gameplay consequence for eligible single-hit units, rather than a purely read-only probability reference. The attack itself, queued commands, natural enemy damage and BB code remain unchanged.

Examples: Eze original unit #40011 has one normal hit and is eligible. Vargas #10011 has three normal hits and is **strictly excluded**, because calculating independent per-hit criticals from the current synthetic lumped damage routine would invent native timing. Multi-hit normal attacks, BBs/SBBs/UBBs, synthetic enemy strikes, buffs, critical immunity and enemy resistance remain unchanged. The exact 2022 underlying ATK/DEF/critical ordering and hit-flooring have **not** been fully reconstructed; the 10%/150% base rule is original, its application to the existing single-event DEMO damage calculation is the supported approximation.

The extension is loaded after v92 without changing any original source table. A small optional battle-only inspection panel reports observed critical and noncritical sourced single-hit attacks; it has no effect on damage beyond the rule above.

## Stability contract
- `P.version=7`, `bf_global_offline_demo_v7`, existing keys, summoned/evolved units and save content unchanged. No writes to `P`, `localStorage`, inventory, quests or stored BB mastery.
- Android package `org.bravefrontier.offline`, debug signing keystore, offline manifest, all previous v91–v92 mechanics retained.
- Unknown/malformed identities are fail-closed, temporary battle state resets with battle, absent module retains existing damage calculation.
- New headless Chromium test covers exact critical roll threshold, hit-count gating, real combat damage, ordinary hit, multi-hit exclusion, training/reset, duplicate injection and no save mutation. Signed APK test checks packaging/source and offline identity; inherited CI remains required.
- **Only promote an exact green GitHub Actions SHA with uploaded signed APK**. No claim of physical Android install verification.

Next gameplay priorities: proper per-hit native attack damage and crit/spark timing, original mission-to-monster wave mapping/AI, BC/HC pickup distribution, actual original stat/damage formula and rewards.
