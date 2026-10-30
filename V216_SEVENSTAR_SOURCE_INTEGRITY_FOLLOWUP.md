# v216 — Seven-star source integrity adversarial follow-up

**Status:** synthetic, read-only tests and validation input hardening only. There is no new 7★/8★ playable form, source import, live evolution, player inventory, save mutation, APK asset, signing or gameplay modification.

Addresses independent Claude feedback on v215 PR #148.

## Adversarial source-identity checks

1. **Coordinated edits:** Change the same unit material ID in *both* the v130 typed-row manifest and v127 source manifest, keeping the two declared source SHA fields unchanged. The ordinary row-by-row join still agrees, but the independently recomputed canonical v130 rows digest must now reject the pair. This pins the canonical row checksum guard.
2. **Complete six-element 8★ set:** Duplicate an existing 8★ form into another slot in *both* synthetic source manifests. Replace the synthetic declared typed-row SHA and (only within the test) patch the expected checksum to match the corrupt row list. All other joins and row types remain consistent; the six-element 8★ identity requirement must still reject the duplicate/missing form.
3. **Malformed source manifests:** Non-dict v127 rows, `originalEvo = null`, malformed typed material arrays and non-list v130 rows must raise a consistent `ValueError`. The v215 audit now validates shape before dereferencing any record.
4. **Positive behavior and no-save boundary:** The twelve verified original starter recipes still pass and `original2022EvolutionAuthorized` stays false. No production HTML is imported, executed, or modified.

## Provenance and interpretation limits

The original 2022 master ZIP SHA-256 `69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9` was authenticated in earlier owner-side research, **not re-opened or re-hashed by this public workflow**. The v130 typed-row canonical digest is independently checked against the committed source rows; v127 `canonical12SourceSha256` and v130 `verifiedInputCanonical12Sha256` are cross-checked **as declared source provenance strings**, not independently reproduced from v127 original source-file bytes here. The original asset ZIPs are neither present nor scanned by public CI.

These tests check only synthetic inputs and source fixture stability. A text-level forbidden-keyword scan or byte-before/after comparison is not proof of real owner's save compatibility; the structural read-only nature of the audit supplies the primary isolation. No original EXP thresholds, level/stat rounding, item-inventory transaction, Legend Stone grant, native sprite transforms, authentic BB/LS/SBB behavior or reversible v7 migration has been established.

The term `syntheticResourceCoverage` is intentionally limited to a **test-only resource counter**; it must never be treated as runtime evolution eligibility. All `original2022*Verified` and authorization flags stay false.

## Merge process

This PR is based on v215 PR #148's reviewed SHA and must remain separate until #148 passes its exact-head Android CI and merges. Retarget this PR to the new main and ensure its exact head and code diff match the independent review, plus successful targeted CI and Android CI, a guarded merge and fresh merged-main CI. Any actual game/evolution/save change requires a separate independent Claude review and owner Android backup testing.
