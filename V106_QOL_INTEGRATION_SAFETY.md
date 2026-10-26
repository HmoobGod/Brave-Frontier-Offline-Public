# Brave Frontier Global Offline — v106 Integration Safety Gate

**Scope: regression hardening only; application version remains 105.00.**

Main baseline: v105 cumulative QoL merge \`dbf6beb8acaa5fe8a859b1093ca0af0980ad7c09\`.

- Source audit covers all nine optional JS modules implementing ten requested QoL areas (v97–v105).
- Verify independent Java WebView injection, ascending version order and the pre-existing source-backed critical modules' precedence.
- Prevent accidental changes to v7 game save / roster / battle / rewards from read-only QoL modules.
- Squad presets retain the only intentional, validated native saveProgress() call and rollback on failure.
- Enforce 64-KiB resource bounds, no network calls, same original Android package and signing secret configuration.
- After APK generation compare every packaged optional JS module byte-for-byte to its checked-in source.
- Original save key remains \`bf_global_offline_demo_v7\`; optional settings use independent local keys.

The following are **not** proven by automated tests: Android live touch UX, migration of real user progress, on-device force-stop persistence, save import/export picker behavior, long-session stability.

## Next original-mechanics research priorities

1. Recover source-qualified native BC/HC **pickup distribution and BB/HP effect** before activating the existing uncollected drop-roll ledger.
2. Recover 2022 Global battle enemy AI, wave formations and historical reward/drop tables; do not substitute 2014 data when equivalence is unverified.
3. Recover full damage, spark, overkill, SBB/UBB interaction and original BB mastery rules.
4. Expand the current playable roster and story beyond the 72 playable forms / 106 archived quests when all prerequisite verified sprites/data are available.

Changes to authentic mechanics must remain separate from DEMO approximations. No source-unspecified rates or gameplay behavior are introduced by this checkpoint.
