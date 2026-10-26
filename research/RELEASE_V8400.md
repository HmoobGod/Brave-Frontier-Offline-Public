# Brave Frontier Global v84.00 — Full Original Global Normal Crystal Profile Recovery

**Verified parent:** v83.00 Build #320, commit `a7104fb44588daff60b886cd0fe93077df308d3a`.

## Original 2022 archive audit

Re-read original `mst-decoded.zip` (SHA256 `69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9`) and original F_UNIT_MST_1..2_Ver1084 records:

- **2,258 collectible unit profiles** have unambiguous source normal-attack frame sequence with damage weights summing to 100 and source dropCheckCount 1–55.
- **32 source rows** have inconsistent damage weights and are excluded, never silently normalized. Special unit ID **1** is the non-collectible Summoner identity and is also excluded.
- **4 source rows** had harmless whitespace formatting anomalies, normalized by removing whitespace only (IDs 20926, 51136, 820317, 850347).
- Every one of v82's **71 starter profiles** must agree exactly with v84 source data on hit counts and dropCheckCount.
- Recoverable collaboration units are covered, e.g. original unit #810547 has 12 hits with 4 checks per hit. That does **not** imply every archived unit can be fielded in battle.

Source tuples are stored in an 11.4KB lossless base36 unit-ID delta stream in `bf8400_original_normal_crystal_checks.js`. A FNV-1a checksum `690fb10d` and schema/provenance audit metadata protect and document source fidelity. Runtime module is below Android's 64KiB per-resource limit.

## Scope

The new read-only module `BFGlobalAllNormalCrystalChecksV8400` exposes `lookup` and deterministic `rollNormal` for 35% BC per original drop check and 10% HC per original damage hit, with optional 2x overkill. Missing/malformed original data returns null. It **does not** change live battles, enemy AI, BB gauge, HP, crystal allocation, inventory, quests, or v7 saves. Enemy resistances, buffs, pickup distribution and native rates remain unresolved. All existing gameplay and v82/v83 services remain installed and unchanged.

**Release requires full green GitHub Actions AND uploaded signed APK artifact.**