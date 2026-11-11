# v362 — Safe evolution-readiness filters and Training navigation

## Scope

Read-only upgrade to the existing `bf10400_qol_evolution_needs.js` panel, not a rewrite of the original 2022 evolution mechanics.

- Filter existing owned unit source-recipes by all, all archived material IDs held, missing material IDs, or conservative DEMO cost/level readiness.
- DEMO readiness requires the existing `BF_EvolutionRoadmapV039.plan(baseId)` to match **both** current form and selected source target, valid nonnegative integer DEMO Zel and EXP, level >=2 using the existing `demoLevel`, and enough materials for the matched live Roadmap recipe. Missing/malformed/throwing providers always classify as **not verified**, not ready.
- An optional Training shortcut opens existing Units -> Training using existing router only; it never trains, spends Zel/shards, evolves units, or saves.
- The original 2022 archived material list still distinguishes source reference IDs from separately implemented DEMO evolution requirements. Even "DEMO costs/level covered" is a preliminary informational status; the Evolution Lab remains authoritative for final restrictions.
- CSS uses >=44px filter and button targets, accessible labels, DOM text insertion only (no unsafe HTML markup), no hidden source claim.

## Tests

Existing registered `test_bf_qol_evolution_needs_v10400.py` extends a disposable Chromium fixture: original source material multiplicity, Demo level/cost readiness on synthetic roster, changing a filter when material counts change, no-results fallback, idempotent module insertion, Training navigation and no P mutation by UI controls. Packaged `test_bf_packaged_qol_evolution_needs_v10400.py` confirms the shipped source and stable signing/offline/Android identity. Full signed Android/Chromium/packaged CI required on exact head.

## Safety and merge gates

No save-schema/owner-data writes, no automatic gameplay actions, no original enemy/NPC AI alterations, and no Android manifest, signing, native app identity, or permission changes. Keep as a draft until independent Claude exact-head APPROVE and full signed GitHub CI green. Do not merge while upstream integration is unsafe. Owner's working APK and `bf_global_offline_demo_v7` save remain untouched. No full actual-demo-evolve button automation in this patch; that requires separately reviewed transactional coverage.
