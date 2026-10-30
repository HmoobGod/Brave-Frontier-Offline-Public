# v195 — EXP save-migration preflight for original 2022 Brave Frontier Global

**READ-ONLY / SYNTHETIC DATA ONLY. No actual save is loaded, written, migrated, or uploaded. No gameplay/Android code changes.**

## Why v195 is needed

The current offline game's **canonical v7 save** stores DEMO `P.unitExp`.
The actual DEMO threshold to enter level `L` is
`5 × L × (L−1) ÷ 2`, with **hard stop at level 99**. For example, Lv99
requires only **24,255** DEMO EXP.

The owner's authenticated 2022 Global `F_UNIT_MST` provides `expPatternId`
10/15/20 for the 72 playable source forms (42/24/6), their original
`unitMaxLevel` (12, 30, 40, 60, 80, 100) and their exact Lv1/Lord-max
stat endpoints. It does **not establish** verified original 2022 cumulative
EXP thresholds, type growth, rounding, or safe conversion of saved DEMO EXP.

v194 cross-references numerical EXP rows from **DecompFrontier's
experimental v2.19.6.0 server** at pinned commit
`7cc0ebd3be79ca561874f70224c3ed924224583b`, **NOT** the authenticated
owner 2022 Global source. Its numerical rows may represent incremental EXP,
but native semantics and 2022 version parity are **unverified**.

## Code and safety

`audit_bf_2022_exp_save_migration_preflight_v19500.py` reads only the
committed original 2022 v115/v116 and external candidate v194 JSON manifests.
It checks exact source hashes/flags and all 72 original unit IDs and source
caps before computing **432 synthetic examples** (72 forms × six DEMO
sample values). An optional `--output` writes a research-only JSON report
**outside** the repository. It never reads a save file, never updates
`index.html`, Java, an APK, or `P.unitExp`.

For each synthetic unit/EXP pair, the report separates:

- Existing level from **the actual DEMO formula**.
- Archive-mode battle cap using its **source-verified max level**.
- Hypothetical level **if** the same DEMO numeric EXP were reinterpreted
  using the external candidate table.
- An illustrative fraction-preserving candidate XP value only if safely
  below both the original max-level cap and DEMO level 99. That value is
  **not an approved player migration result**.
- An explicit ambiguity flag at the cap (saved DEMO EXP can exceed the
  max-level threshold and still mean level-capped).
- `native2022ExpMigrationAllowed: false`, `writesUserSave: false`, and
  `original2022ThresholdsAuthenticated: false` on **every** row.

Examples:

| Reaching level | DEMO saved EXP threshold | External pattern 10 hypothetical | Pattern 15 | Pattern 20 |
|---|---:|---:|---:|---:|
| 2 | 5 | 10 | 15 | 21 |
| 5 | 50 | 328 | 492 | 658 |
| 12 | 330 | 4,115 | 6,173 | 8,232 |
| 30 | 2,175 | 46,442 | 69,664 | 92,883 |
| 60 | 8,850 | 274,185 | 411,280 | 548,366 |
| 99 | 24,255 | 974,938 | 1,462,408 | 1,949,874 |
| 100 | **not reachable** | 1,000,000 | 1,500,000 | 1,999,997 |

All external columns are **hypotheses under an unverified incremental-row
interpretation** and **not** measured original 2022 global thresholds.

`test_bf_2022_exp_save_migration_preflight_v19500.py` validates DEMO
thresholds, all 72 original source forms, the 12 original Lv100 forms,
432 synthetic comparisons, safe output location, report reproducibility
and eight corrupt-source/incorrect-provenance rejection probes. Byte hashes
of input data and `index.html` must be unchanged.

## What is NOT done

- No editable native EXP option, level cap lifting, 7★/8★ evolution unlock,
  stat-rounding change, source-WAVE or enemy AI changes.
- No conversion of old saves, no write to v7, no extra storage keys, no
  inference of native 2022 EXP from experimental server values.
- No Android APK or new gameplay UI created in v195.
- No evidence that a raw level or percentage is a sufficient reversible
  conversion. Over-cap DEMO experience, discrete rounded increments,
  evolved forms and older APK downgrade must be handled explicitly.

## Remaining release gates

1. Obtain and authenticate exact original **2022 Global** EXP pattern table
   with per-level semantics, including IDs 10/15/20 and level 100.
2. Validate original stat curves/unit type bonuses, intermediate level
   rounding and evolution level transfer.
3. Design a separate opt-in migration that **preserves the original DEMO
   saved XP**, has downgrade and import/export semantics, and does not
   reinterpret existing values silently.
4. Require independent Claude review of any live XP or save mutation,
   exact-head CI and fresh merged-main CI, then owner Android in-place
   upgrade tests with a backed-up save.
5. Treat historical and external curve values as candidates until the
   original 2022 authenticity gate is closed.

**v195 merge scope:** Research scripts, tests, documentation and one CI line;
no functional Android file or save schema changes.
