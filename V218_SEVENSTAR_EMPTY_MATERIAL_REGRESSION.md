# v218 — Claude v217 non-blocking regression follow-up

This is a **test-only** follow-up based on the verified v217 merge `dd7ec6d8055501868f0319081b068444bedaf2d0`. It resolves Claude's v217 exact-head review nits N1 and N2 without altering the original source or any gameplay.

## What changes
- Extend the existing `test_bf_sevenstar_complete_elements_v21700.py` malformed `originalEvo.materialSlots` regression inputs to include the **empty list** `[]`, requiring the exact `ValueError("malformed original evolution source")`.
- Clarify how `duplicate_form` isolates the full six-element 7★/8★ roster guards: coordinated synthetic changes bypass the manifest join, a recomputed declared digest and temporary `ROWS_SHA` bypass the pinned checksum guard, while independent six-element completeness still rejects duplicate forms.
- All v215/v216/v217 positive and negative tests remain running in the existing seven-star workflow. A previous Claude mutation probe found that deleting the empty-list guard passed v217's prior tests; the new `[]` expectation is designed to fail on that mutation.

## Hard boundary
No modifications to `audit_bf_7star_typed_evolution_preflight_v21500.py`, production source manifests, Android Java/HTML/JS/resources/signing, save key/schema, gem/Imp rewards, quest mechanics, or real playable evolution. No 7★/8★ unlock. This is source-level test coverage, **not** Android owner-device or save migration proof.

## Independent review and merge
Obtain independent Claude delta review against the exact v218 head, successful exact-head targeted source CI and full Android build CI, then merge with a head-SHA guard. Verify post-merge source and Android CI on the actual main merge commit. No promotion to Current.
