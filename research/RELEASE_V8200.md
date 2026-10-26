# Brave Frontier Global v82.00 — Decoded Original Normal-Attack BC Drop Checks

**Parent:** v81 crystal-rate core candidate `3f4d19e9a8b678648837bbd253ad178b9f1d1e1a`. Do not promote either version without exact successful CI and Android signed debug artifact.

## Verified major archival discovery

Further inspection of the original supplied 2022 Global translated master **`F_UNIT_MST_1_Ver1084.json`** and **`F_UNIT_MST_2_Ver1084.json`** revealed a readable, source-named **`dropCheckCount` column** next to `damageFrames`, `effectFrames` and `element`. Source part SHA256 values are retained in `source_data/bf_global_2022_normal_crystal_checks_v8200.json`. All **71 valid playable normal-attack profiles** supported by the existing v700 hit reference are joined by exact `unitId`, with source `dropCheckCount` parsed as a positive integer. For example:

| Original unit ID | Hits | Checks per hit | Total normal BC checks |
|---|---:|---:|---:|
| 10011 Vargas | 3 | 2 | 6 |
| 40011 Eze | 1 | 8 | 8 |
| 30015 Lance | 5 | 5 | 25 |

The original community mechanics references distinguish BC drop checks per hit from HC chances per actual hit: <https://bravefrontierglobal.fandom.com/wiki/Drop_Rate> and <https://bravefrontierglobal.fandom.com/wiki/Drop_Rate_Boost>. This discovery **resolves the normal-attack BC checks uncertainty described in v81**, but does not resolve BB/SBB drop checks, enemy resistances, hit multipliers, leader passive bonuses or pickup distribution. Malformed-source unit #10023 remains strictly excluded because archived attack weights total 130 rather than 100.

## Runtime integration

A new small read-only `BFGlobalNormalCrystalChecksV8200` service exposes exact original per-hit and total normal BC checks, expected base BC/HC, and deterministic base-rate sampling using the already-tested v81 calculations (35% BC per check, 10% HC per hit, doubled by overkill where the caller supplies a verified overkill flag). v81's `expected(unitId)` now automatically uses those original source checks when available, without generating fake checks for unsupported forms. This is source-faithful normal attack **drop production math**, not yet implemented crystal collections: the engine does not change BB gauges, recover HP, distribute dropped crystals, alter enemies, write inventories or grant rewards without corresponding recovered mechanics.

Tests validate all 71 exact source rows, independent source SHA, total normal BC checks, deterministic RNG and overkill, missing ID, #10023 rejection, module idempotency, P/localStorage/gameplay stat isolation, no INTERNET, same Android signing and complete inherited gameplay/APK suites. Neither BC check count nor HP data is guessed.
