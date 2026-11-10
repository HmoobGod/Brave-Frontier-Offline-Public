# v333 — Fail closed on unknown living-enemy ATK/DEF focus ranks

## Bug
The playable v3100 manual Focus panel previously ran `living.filter(e => Number.isFinite(e[key]))` for Highest ATK / Lowest DEF. If a live foe's attack or defense was absent, the focus planner could silently ignore that foe and issue a real native player targeting order to another foe, even though the correct ranking was unknowable.

## Fix
Reject an ATK/DEF ranking when **any living enemy** lacks a finite value for the chosen stat. Do not alter HP-based target ranking, elemental source matching, native actor slots, Auto Battle AI, battle arithmetic, quest progression, saved game or enemy AI. Focus buttons now disable when their proposed strategy has no eligible validated target, including missing stats or absent source-known elemental advantages.

## Acceptance
Expand the real-page Chromium focus test with a valid two-enemy fixture where one living foe has unknown ATK/DEF. Confirm both affected strategies return null, both direct focus and squad queue actions reject, buttons are disabled, valid HP ranking stays usable, no player's orders/target change, no turn starts, P and canonical saved bytes remain unchanged. The packaged Android regression checks the validation and UI gating. Exact-head signed Android+Chromium+save CI and review are required before merge. Four-file, separate draft PR on #325, disjoint from pending #332.

This is a **DEMO manual focus safety correction**, not recovery of historical 2022 enemy statistics or original native enemy AI.

## v333R1 — dynamic UI eligibility correction
The initial v333 source disabled invalid focus buttons, but its cached refresh signature tracked only the *selected* strategy and elemental focus. When the selected strategy stayed unchanged, losing a different foe's ATK/DEF could leave other focus buttons visually enabled. The refresh cache now also contains every strategy's validity, and a Chromium regression checks valid → unknown → valid stat transitions without state/save writes.
