# v118 — 2022 Global EXP Pattern and Unit Type Source Gates

This is a **source-only fidelity regression** built on the verified 2022 archival v116 catalog. It does not replace the current offline DEMO leveling or battle stat implementation.

## Verified original-source metadata

- All **72 playable unit forms** retain the exact `unitExpPatternId` from the archived `F_UNIT_MST_1/2_Ver1084` masters.
- Exact distribution: **10 = 42 forms**, **15 = 24 forms**, **20 = 6 forms**. First-series starters and alternate forms use 10; the second-series initial four stages use 15; their six 6★ final forms use 20.
- Their exact original `unitMaxLevel` continues to match the v115 cap catalog.
- Six rows from `F_UNIT_TYPE_MST_Ver52` are checked **field-for-field**, including raw HP/ATK/DEF/REC ranges, original acquisition-chance strings **23/23/22/22/10/0**, and uninterpreted `unknownRaw` values. The Rex normal-acquisition chance is zero.
- Both underlying archive/table SHA256 provenance values are pinned in the regression.

## Explicitly not established

Pattern IDs **are not numeric XP curve tables**. Type raw strings and chances **are not a proven RNG, per-level stat-roll rule, unit assignment or rounding algorithm**. In particular, `unknownRaw` is intentionally uninterpreted. We do not claim original middle-level stat progression, unit type behavior, XP migration, or damage formula recovery.

## Compatibility boundary

No Android Java, gameplay, asset data, save schema, signing, or unit EXP values are changed. `P.version === 7` and the existing `bf_global_offline_demo_v7` local-save key stay intact. Verified v117 generated unit stat mapping and all prior CI tests remain active.

**Next:** obtain verifiable source-derived cumulative XP thresholds for patterns 10/15/20 and independently verified Lord intermediate-level stat examples. Add a read-only comparison against the DEMO level mapping before proposing a save-safe, opt-in runtime adapter.
