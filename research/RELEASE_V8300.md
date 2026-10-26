# Brave Frontier Global v83.00 — Original BB/SBB Crystal Check Source Recovery

**Verified parent:** v82.00 Build #318, commit `1fd3d0da9d84917c173f4454f952ef572016cb81`.

## Original source evidence

The supplied archived `mst-decoded.zip` (SHA256 `69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9`) contains F_SKILL_MST_1..9_Ver1535.json, all with a source-named `dropCheckCount` field. Exact F_UNIT_MST unit links `bbId` and `sbbId` were joined to the 71 already validated v82 normal-attack unit IDs.

- **71 BB** links and **12 SBB** links resolve uniquely to source skill IDs.
- **61 BB/SBB** records have structurally simple `damageFrames`; **13 are healing/support** effects (skill type 2/5 with allied targets), NOT BC-producing attacks. Only **47 offensive BB and one offensive SBB** pass the source skill-type + enemy-target + simple-group gate for provisional per-target checks.
- **22 complex BB/SBB groups** have `@` multiplexed frames; their per-event counts are not inferred.
- Source examples: Vargas #10011 BB skill #10011 has five simple damage events with one drop check each; unit #60025 SBB skill #160025 has one simple event and source dropCheckCount 25.
- All nine skill-table SHA256 values, both unit-table SHA256 values and each matched skill ID are recorded in `source_data/bf_global_2022_burst_drop_checks_v8300.json`.

## Behavior and limits

`BFGlobalBurstCrystalChecksV8300` is read-only and dependent on the verified v81/v82 reference cores. It exposes source checks and *provisional reference* per-target BC counts only for the 48 simple, source-classified offensive damage groups; 13 healing/buff groups explicitly cannot roll BC. It never modifies live HP/BB, pickups, saved progress, enemy resistances, inventory, quests, or rewards. Native skill event timing, target multiplicity and modifiers remain unresolved. The client still uses its existing demo fallback where original gameplay formulas are unavailable.

The regression suite validates 83 skill joins, unknown/support fail-closed behavior, determinism, source provenance, module idempotency, no progress changes, load order, signed Android package identity and the inherited offline/save tests. **Promote v83 only if GitHub Actions completes successfully and uploads an APK artifact.**
