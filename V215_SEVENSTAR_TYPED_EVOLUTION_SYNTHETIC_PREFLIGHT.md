# v215 — Source-authenticated starter 7★ / 8★ evolution transaction preflight

**Status: code/test-only synthetic research. No new playable units, inventory, game logic, Android asset or save migration.**

## Source-backed facts preserved

The owner-verified original 2022 Global master is pinned to \`mst-decoded.zip\` SHA-256
\`69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9\`.
The existing v127 and v130 source manifests preserve twelve typed evolution recipes for the six starter elements:

- Six 6★ → 7★ evolutions: original target IDs \`10016\`, \`20016\`, \`30016\`, \`40016\`, \`50016\`, \`60016\`; 1,500,000 Zel, zero Karma, four **unit** material slots and one **original item** slot ID \`110100\` (Legend Stone).
- Six 7★ → 8★ evolutions: corresponding \`*017\` target IDs; 3,000,000 Zel, 1,000,000 Karma, seven unit material slots and one Legend Stone slot.
- Duplicated unit material IDs are intentionally counted by source-slot multiplicity rather than collapsed into a set. A Legend Stone *unit material* with the same numeric ID never satisfies the original typed item requirement.

The independent v137 source research found historical exchange schedules for Legend Stones, but an original 2022 player inventory implementation and active acquisition rules are not established by those schedules.

## What the code actually does

\`audit_bf_7star_typed_evolution_preflight_v21500.py\` provides two **read-only pure functions**:

1. \`recipe_rows()\` joins both original manifests and validates their source hashes, source-preserved typed slots, starter lineage, source currency costs and six-element 7★/8★ sets. It rejects mismatches and corruption.
2. \`preflight(target, owned_forms, unit_materials, original_items, zel, karma)\` accepts **caller-supplied synthetic Python test data only** and returns missing unit materials, missing original items and source currency/owned-form coverage.

This is *not* a \`P\` / \`P.materials\` parser and cannot represent the real saved inventory. An affirmative \`syntheticResourceCoverage\` **never** means a valid live evolution; \`original2022EvolutionAuthorized\` stays \`false\` unconditionally. The original 2022 EXP/level, visual transforms and inventory semantics remain unverified.

\`test_bf_7star_typed_evolution_preflight_v21500.py\` covers all twelve source recipes, distinct typed inventory maps, multiple copies of the same material, missing Legend Stones despite a matching number in the other inventory, duplicate owned targets, absent prerequisites, insufficient Zel/Karma, negative/non-integer resources, unknown targets, source hash and manifest corruption, deterministic results, and byte-identical 2022 source fixtures/production HTML after the run.

## Remaining gates to playable 7★

1. Authenticate original 2022 Global EXP thresholds, level/interpolation/rounding and evolution level handling (v193–v195 research currently shows only historical/experimental candidate curves).
2. Establish actual original item inventory and Legend Stone grant/exchange semantics separately from unit-material inventory, without guessing inventory storage fields.
3. Validate original sprite rendering/transforms and BB/LS/SBB/UBB game behavior beyond the existing temporary v147–v150 test actors.
4. Design a reversible, backwards-compatible v7 save transition; run browser, packaged APK and owner Android upgrade/save-backup tests. Claude must independently approve any gameplay/save changes.

This research patch must not change \`app/src\`, runtime encounter data, v7 saves, original/personal Gems, Imp rules, signing, nor existing 72 playable form guarantees. The narrow source-only CI regression is supplemental to the exact-head full Android build and post-merge main build. Code review is requested before merge.
