# v121 — Original 2022 EXP-pattern identifiers for every archived unit

All **2,291** records in the existing 2022 Global Unit Encyclopedia now have source-verified **unitExpPatternId** values. These are *not* numeric experience curves.

**Primary source:** user's **mst-decoded.zip**, SHA256 `69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9`; translated files F_UNIT_MST_1_Ver1084.json and F_UNIT_MST_2_Ver1084.json (source hashes recorded in V120_ALL_2291_ORIGINAL_STAT_FIDELITY.md).

- Projection of 2,291 sorted (unitId, unitExpPatternId) pairs SHA256: `b897f8588d450a111206f16b4b09f5a5d8f3c3750e5f2e24d4ddd9ca0c84c48c`.
- Sorted unit-ID SHA256: `19a96b6d8987a7fb3099fc302185020702e6da248f9493f47268cb4ccba88c89`.
- A compact 573-byte, two-bit-per-record original-source map has SHA256 `29b69acf743c50267c92c1022ab7c0f5032bcd22494974afcc100c54c27b4c64`.
- Codes 0 → pattern 10, 1 → pattern 15, 2 → pattern 20; invalid code 3 is rejected.
- Across all unit records: pattern 10 = **248**, pattern 15 = **245**, pattern 20 = **1,798**. All 72 currently playable forms match the v116 original reference.

The existing encyclopedia displays this original-source *pattern ID* but explicitly notes that **numeric EXP thresholds have not been verified against the 2022 Global release**. The DecompFrontier curve and some historical fan tables disagree by small amounts; neither is activated.

There are NO changes to battle experience, leveling, saved P.unitExp, unit recruitment, active squad, RNG, Android signing or localStorage schema. The small UI resource is optional. Existing unit records are still not automatically recruitable or playable.

**Regression:** Python and Chromium test_bf_original_all_unit_exp_ids_v12100.py validates all 2,291 mappings with source-independent SHA256 digests, 72 unit joins, UI rendering and save-v7 snapshot equality.
