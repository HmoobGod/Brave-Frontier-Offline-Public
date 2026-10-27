# v120 — Fidelity gate for the existing 2,291-row original Global encyclopedia

The game **already** bundles a 2,291-row read-only original Global unit encyclopedia. Rather than duplicate or replace its data, this checkpoint verifies its original **unit ID, max level, level-one HP/ATK/DEF/REC, and Lord max-level HP/ATK/DEF/REC** values against the owner's independent 2022 \`mst-decoded.zip\` source.

- Owner ZIP SHA256: \`69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9\`.
- Originals: \`3-mst-translated/F_UNIT_MST_1_Ver1084.json\` (SHA \`1146f09489a07b9187cd3f04bf7dc3ef3bb74e35385869534671af95bf8ea645\`) and \`F_UNIT_MST_2_Ver1084.json\` (SHA \`0696ccda59fccf48598c5267eaeb8a306e994618384151cead38cec6a9195b2b\`).
- 2,291 unique original records, including NPC/special/material/unit entries: not all are gameplay-ready. 127 records are fixed at level one; one exceptional source entry is capped at level 500.
- SHA256 of canonical sorted source records (10 integer fields: ID, max level, original base and Lord endpoints): \`a10b45bb5fa10f555cbbcfb31793f65b9a1a8c3f702611b5ea66d7a1be644914\`.
- Original 2022 \`unitExpPatternId\` distribution across all 2,291 master records: pattern 10 = **248**, 15 = **245**, 20 = **1,798**. Those pattern fields are not included in this particular stat-endpoint digest. Numeric threshold tables are **still externally sourced candidate data**, not confirmed identical to 2022 Global.
- The 72 currently supported original playable forms' max levels, 4 base and 4 Lord endpoints are separately checked against the source-verified v116 catalog.
- All data checks occur in Python CI; the existing compressed original catalog, its archive viewer, live combat, Android Java, signing, EXP semantics and serialized save-v7 fields are untouched.

**Purpose:** guard the already-recovered original encyclopedia against accidental stat or level-cap drift while extending research beyond the first 72 forms. This does **not** unlock the other 2,219 entries, recover native per-level stat growth, or enable an EXP migration.

**Future:** source-test representative mid-level Lord values and independently version-match external \`M_UNIT_EXP_PATTERN_MST\` numeric thresholds before considering an opt-in native progression adapter.
