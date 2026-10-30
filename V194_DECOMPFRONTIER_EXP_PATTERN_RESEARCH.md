# v194 — Original 2022 EXP pattern IDs crosschecked against DecompFrontier data

**READ-ONLY RESEARCH. No native 2022 EXP threshold has been authenticated.**

## Discovery and provenance

The experimental <https://github.com/decompfrontier/server> server (README:
**Brave Frontier v2.19.6.0**, not an authenticated owner 2022 Global master)
publishes `deploy/system/unit_exp_pattern.json`, a deobfuscated-format
original-style data file with exactly **804 level records**: 201 records each
for pattern IDs **10, 15, 20 and 25**.

Pinned external source:
- Repository: `decompfrontier/server` (**upstream AGPL-3.0; attribution retained**).
- Exact commit: `7cc0ebd3be79ca561874f70224c3ed924224583b`.
- File Git blob SHA-1: `c109ff5059f3fad457d95ad196552d601716d4db`.
- Path: `deploy/system/unit_exp_pattern.json`.
- Direct pinned source:
  https://github.com/decompfrontier/server/blob/7cc0ebd3be79ca561874f70224c3ed924224583b/deploy/system/unit_exp_pattern.json

**Actual repo source was opened and inspected**, not merely inferred from a
wiki. The obfuscated keys are `JYFGe9y6` (array), `5UvTp7q1` (pattern
ID), `D9wXQI2V` (level), and `grKTq15A` (numeric EXP row value).
The 25 pattern is 201 zero rows; it is not applied. Patterns 10, 15 and 20
have complete consecutive levels 1–201. The compact research fixture
retains only their first 100 numeric row values because the currently
playable 72 original 2022 source forms have `unitMaxLevel` ≤100.

## Surprising pattern match, not conclusive 2022 proof

The owner's authenticated original 2022 master (v116/v118) confirms precisely
**42 playable forms with ID 10, 24 with 15, six with 20**, but includes no
validated **2022 EXP threshold table**. The external emulator candidate
fixture has the same three IDs and the following raw record values:

| Pattern | L2 row value | L3 row | L4 row | L5 row | L100 row | Sum of rows 1–100 |
|---|---:|---:|---:|---:|---:|---:|
| 10 | 10 | 48 | 102 | 168 | 25,062 | 1,000,000 |
| 15 | 15 | 72 | 153 | 252 | 37,592 | 1,500,000 |
| 20 | **21** | 96 | 204 | 337 | 50,123 | 1,999,997 |

This establishes **external** pattern-20 row at level 2 = 21, a concrete
candidate explanation for the older community label "initial 21 EXP".
It **does not prove** the owner's original 2022 Global client uses the same
rows, units, rounding, UI or server-level semantics.

If the row values mean *incremental* EXP per level, their running Lv5 totals
are 328 / 492 / 658, compared to older community Lv5 cumulative examples
329 / 492 / 658 in v193. The **one-EXP discrepancy for pattern 10**
demonstrates why older-era data should not be silently substituted.
Neither the incremental interpretation nor any specific 2022 Lv100 threshold
is established by the external table alone.

## Actual v194 changes

- `source_data/bf_global_external_exp_pattern_candidates_v194.json`:
  an attributed, **compact numerical data excerpt** (300 raw level values,
  provenance and flags), **not** the upstream C++ server source code.
- `audit_bf_external_exp_patterns_v19400.py`:
  checks old authentic 2022 source pattern distribution, external candidate
  sample values, row sums, external SHA, separate cross-era hypotheses;
  optional `--upstream path/to/unit_exp_pattern.json` verifies an entire
  externally obtained file is **byte-exact to the pinned upstream Git blob**
  and all **804** rows. The tool never fetches data over the network.
- `test_bf_external_exp_patterns_v19400.py`: reproducible validation,
  deterministic read-only output and seven defensive negative probes
  (including source mismatch, altering pattern 20 to 20 EXP, malformed
  length, inferred native-2022 claims and blocked repo overwrites).
- Existing GitHub Actions test stage runs new test after v193. No data
  integration into Android, Java, `index.html`, animations, unit leveling,
  `P.unitExp`, original Gem/Imp ledgers, or v7 saved progress.

## Native leveling acceptance gates (still OPEN)

1. Authenticate the exact original owner's **2022 unit EXP pattern master**
   or original client protocol/logic against these 804 external rows.
2. Establish whether raw `grKTq15A` represents cumulative level threshold,
   per-level increment, or another level field for **that exact 2022 build**.
3. Reconstruct **Lv1–100** XP and type-specific stat interpolation separately;
   pass cross-era discrepancies and the 12 original Lv100 forms.
4. Design safe existing `P.unitExp` migration with 2022/DEMO explicit mode
   and reversibility, including user owner-tested v188/v191/v192 data.
5. Independent Claude review **before enabling any gameplay EXP migration**;
   exact-head feature CI and merged-main CI for research additions.

Do not present these as the original 2022 XP values in the playable UI.
The server repository's code is licensed **AGPL-3.0**; this audit imports only
a small numeric source-data excerpt, not C++ code. Credits and the upstream
source/license are explicitly retained. Review reuse and redistribution
requirements if later importing server code or a complete source file.
