# v219 — Independent v127 original seven/eight-star source manifest file byte pin

**Status:** source-only integrity hardening; no playable 7★ or 8★ evolution unlock, original inventory, EXP, animation, Android or save changes.

## Why

Claude's independent v217 review noted that the prior audit compared the v130 typed rows to the v127 twelve-form data and checked the v127 self-declared `canonical12SourceSha256` without independently hashing the complete v127 file. That canonical digest intentionally excludes metadata such as `sourceFiles`, `ownerAssetPacks`, `caution`, animation/source-art metadata and JSON formatting.

The exact complete UTF-8 v127 file currently committed at v218 main `82cdc63f98f1318971d595aef211574bb1fba857` independently hashes to SHA-256:

`2fb14fda2d9a291df756d0e2332b68ded1929d8618e50159e899b68b5829146e`

This digest is **not** the separate 12-row canonical tuple digest `dcd3fb0f3d57b44880088f42c87409e3588a24a183ec866095ea0dbeae57bcbd`, nor a newly authenticated original 2022 source ZIP hash.

## v219 code

- `audit_bf_7star_typed_evolution_preflight_v21500.py`: on **on-disk default v127 manifest loading only**, hash `MANIFEST.read_bytes()` with SHA-256 and fail closed as `ValueError("source manifest file checksum mismatch")` before JSON parsing if it differs. Keep explicitly provided synthetic in-memory manifests supported and subject to their existing structural/canonical checks; the byte pin **does not authenticate arbitrary injected Python dictionaries**.
- `test_bf_sevenstar_manifest_file_pin_v21900.py`: independently verify the expected raw digest, assert successful authentic 12-row lookup, mutate only non-recipe `caution` metadata or JSON whitespace while keeping canonical source rows and their self-declared digest unchanged, and assert that both temporary on-disk fixtures are rejected with the precise checksum error. Verify explicit in-memory fixture calls remain usable, and the production source fixtures remain byte-identical after tests.
- `.github/workflows/sevenstar-source-preflight.yml`: include the new test and this document in PR path filters, run new test with v215/v216/v217 source regressions on the exact PR head and every pushed main commit.

## Safety and limitations

No original owner master archive `mst-decoded.zip` was re-extracted; the hash is of **the committed public v127 manifest bytes**, not independent proof of the actual original ZIP's content. The already-recorded owner archive hash remains `69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9`. Any intentional reformat, change to legitimate v127 metadata, or source correction now requires consciously updating this new file pin and re-reviewing the changed source.

There is no runtime Android change, player inventory read, `P.unitExp` migration, asset bundling, Gem/Imp/economy modification, save schema change or newly playable unit. Source-level CI is not the same as Android device testing.

**Remaining blockers to playable source-authentic 7★/8★:** verified original 2022 EXP thresholds and type/level evolution semantics; typed original item inventory/Legend Stone acquisition and transaction behavior; native CGG/CGS transforms, BB/LS/SBB/UBB; reversible save migration and owner upgrade tests.

## Review and promotion gates

Require a separate independent Claude **exact-head** review of v219, successful exact-head source CI and full Android CI, and a SHA-guarded merge only when the current main baseline is stable. Then verify both source and full Android workflows on the actual merge SHA. Never replace the owner's Current APK or saves based on this research-only change.
