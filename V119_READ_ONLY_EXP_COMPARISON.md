# v119 — Read-only original EXP curve comparison

This is a source-research and save-protection regression, **not** native EXP activation.

The owner's 2022 Global archive source verifies 72 original playable unit IDs, all assigned \`unitExpPatternId\` 10 (42 forms), 15 (24 forms) or 20 (6 forms). An independent DecompFrontier/server research snapshot contains a candidate \`M_UNIT_EXP_PATTERN_MST\` level-EXP table for these three IDs (plus ID 25): 201 per-level \`need_exp\` entries per pattern. Provenance: [DecompFrontier source commit 7cc0ebd3](https://github.com/decompfrontier/server/blob/7cc0ebd3be79ca561874f70224c3ed924224583b/deploy/system/unit_exp_pattern.json), blob \`c109ff5059f3fad457d95ad196552d601716d4db\`; raw key names verified against [packet-generator schema](https://github.com/decompfrontier/packet-generator/blob/64b0af3120391624c48099c4cd2b309eb0cbe246/assets/mst/unit.kdl).

**Important distinction:** \`unitExpPatternId=20\` has a second-level requirement of 21, explaining historical community "Base 21" labeling. Do not equate numeric ID and first-level required EXP. The external source version has **not been independently established as identical to the owner's 2022 Global snapshot**, nor have native saved-EXP semantics been recovered.

The CI regression checks all 72 original source assignments, runs positive/failing parser fixtures, compares candidate cumulative checkpoints against the existing *live DEMO* \`demoLevel()\` in Chromium and asserts no change to \`P\` or \`bf_global_offline_demo_v7\` localStorage. No new Android Java, game assets, game networking, type RNG, stat formula, save schema, EXP award, or signing change.

### Optional research (local inputs only)

\`\`\`bash
python test_bf_original_exp_readonly_crosscheck_v11900.py --candidate /path/to/unit_exp_pattern.json --report /new/report.json
python test_bf_original_exp_readonly_crosscheck_v11900.py --candidate /path/to/unit_exp_pattern.json --original-2022 /path/to/independently_verified_original_2022_table.json
\`\`\`

The optional full-source parser fails closed on missing/duplicate levels, non-positive requirements or changed pinned candidate sums. A 2022 table comparison checks all first 100 per-level numbers for all three supported patterns; if files differ, it fails rather than guessing. **No full third-party master or code is redistributed.**

Next prerequisites: recover/verify the owner's original 2022 \`M_UNIT_EXP_PATTERN_MST\`, the EXP-application semantics, save-safe opt-in mapping, mid-level Lord stats and type handling. Leave live leveling unchanged until verified.
