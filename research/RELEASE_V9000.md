# Brave Frontier Global v90.00 — Source-validated Live Crystal Ledger

Parent v89.00 Build #329, exact successful commit `33a1608e6b954ccc6f9f8ab0856d14bc10209948`, signed APK artifact `12592813398`.

The v88 source-aligned normal-attack rolls and v89 strictly supported simple offensive BB event rolls now have a unified current-battle ledger. It reconciles reference BC and HC amounts without changing damage execution. It validates recent event profiles against the exact archived v84/v85 profile tables rather than accepting malformed or unsupported data. Aggregate totals come directly from the complete in-memory v88/v89 counters; the last eight records are displayed as a bounded preview, not presented as full battle history.

**Authenticity boundaries:** 2022 Global `F_UNIT_MST_1/2_Ver1084` normal attack hit/drop-check counts and `F_SKILL_MST_1..9_Ver1535` supported simple offensive BB drop checks are source derived. Base BC 35% per source drop check and HC 10% per hit originate from the existing community-documented rate references. The underlying DEMO battle still uses synthetic action, damage, targeting and enemy logic; no enemy drop resistance, native crystal pickup targets, BB gauge/HP conversion, actual overkill flags, item awards or quest rewards are inferred. DecompFrontier's incomplete MissionStart backend does not establish those rules.

The module is optional and read-only: never modifies `P`, `S`, `localStorage`, v7 saves, HP/BB, unit identity or inventory. It only reads v88/v89 current battle snapshots and presents totals as **uncollected** reference rolls. Original package `org.bravefrontier.offline`, debug signing identity, offline manifest, and older features remain unchanged.

Gates: inherited browser tests, new Playwright normal attack + BB additive session test, source exclusions, no save changes, idempotency, reset, signed APK packaging. Never call a candidate verified until GitHub Actions completes successfully and artifact is uploaded. Android physical device install remains separately unverified.

**Next gameplay gate:** independently establish native recipient/pickup rules and BC-to-BB/HC-to-HP conversions before turning production into collected in-battle crystals. Native 2022 encounter formations/AI also remain high priority.
