# v193 — Original 2022 EXP pattern IDs vs historical level-curve candidates

**Research-only. Does not change the APK, gameplay, player EXP or saves.**

## Why this matters

The owner's original **2022 Brave Frontier Global** source, pinned to
`mst-decoded.zip` SHA256
`69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9`,
contains exactly **72** currently playable unit forms with `expPatternId`
values **10, 15 and 20**. v118 already authenticated the exact distribution
of **42 / 24 / 6 forms** and verified their source IDs and level caps.

Older Brave Frontier community leveling tables instead divide leveling curves
by the **initial EXP needed to reach Lv2**: **10, 15 and 21**.

- Global unit-type classification:
  https://bravefrontierglobal.fandom.com/wiki/Unit_Leveling:Unit_List
- Historical Japanese chart dated 2019:
  https://bravefrontier.gorillawiki.jp/entry/9810
- Independent 2014 table for historical 10/15 classes:
  https://www.online-station.net/mobile-game/153035

These are useful clues but **not an original, authenticated 2022 Global EXP
master nor native client evidence**. The potential correspondence between
the **original 2022 pattern ID 20** and the historical **initial 21 EXP**
class is especially uncertain. The similar numbers 10↔10, 15↔15 are also
not sufficient to prove exact original 2022 level thresholds.

## What v193 adds

`source_data/bf_global_2022_cross_era_exp_candidates_v193.json` pins just
small, historical **cumulative XP samples at levels 1–5**. These figures
are not transplanted into the playable game.

| Historical community class | Lv1 | Lv2 | Lv3 | Lv4 | Lv5 |
|---|---:|---:|---:|---:|---:|
| Initial 10 | 0 | 10 | 58 | 160 | 329 |
| Initial 15 | 0 | 15 | 87 | 240 | 492 |
| Initial 21 | 0 | 21 | 117 | 321 | 658 |

`audit_bf_2022_cross_era_exp_v19300.py` uses the **unmodified v116
source-proven 72-form catalog** to construct a deterministic research matrix
with every original unit ID, original 2022 pattern ID, original max level
and a separately labeled older-era candidate. Each of the 72 rows explicitly
sets `native2022ThresholdsVerified: false` and
`safeToApplyToPlayerExp: false`. In particular, all 12 max-level-100
forms remain in their original 2022 category without inventing the missing
DEMO Lv100 leveling threshold.

The scanner prints a short summary by default; optional
`--output /tmp/research-exp.json` creates a local matrix file. It never
reads or changes player saves or changes Android package/build files.

`test_bf_cross_era_exp_candidates_v19300.py` asserts original master hash
pins, all 72 source IDs, exact 42/24/6 split, sample consistency,
deterministic output, and fail-closed behavior against **six synthetic
corruptions**. It verifies the original source file and prepared HTML
remain byte-for-byte unchanged. It is registered in the existing Actions
test suite after v118.

## Blocking evidence before **any** actual EXP migration

1. Recover a verified **2022 Global level threshold table** for native
   patterns 10, 15 and 20, especially the exact pattern20 ↔ historical
   initial21 relationship.
2. Check representative source-level thresholds at Lv12/30/40/60/80/100,
   and validate original intermediate Lord/type-specific stats/rounding.
3. Develop a reversible or additive migration plan for **existing**
   `P.unitExp` on all owner v124/v188/v192 saves. Never silently
   reinterpret old saved DEMO points as original EXP.
4. Do not change training battles, original quest XP, original 7★/8★ forms,
   roster, Game/Java, signing, APK assets, source archive or Gem/Imp ledgers
   based on historical curves alone.
5. Independent Claude review is required **before any game/runtime/save**
   EXP change. This read-only comparative study requires only exact-head
   Actions CI then a clean merge and merged-main CI.

**Conclusion:** The pattern-20/initial-21 similarity is a **research
hypothesis**, not verified 2022 gameplay. All original battle mechanics and
saves remain as they were in owner-tested v188 and CI-verified v192.
