# Brave Frontier Global v4.00.0-demo — Original 2022 Unit Skill & Historical Battle Dossier

Baseline: v3.50 Build #169, SHA 1d4dae777a32475138a2e1a60520cfe1c2d794f1.

## New source-first feature
* Quest screen: optional **Original Global Battle Dossier**, distinct from the experimental v2.00-v3.50 combat sandbox.
* Read the current six owned/equipped forms (including actual evolution form) and recover each form's official 2022 Global unit name, original element/rarity/base HP/ATK/DEF/REC, original Leader Skill / BB / SBB / UBB / Extra Skill names, source skill IDs, English text, and story when present.
* Display archived original unit thumbnails only where source files exist; no substitute or invented enemy sprite.
* Inspect **21 dated 2014 historical mission wave files** with original filename, Git blob SHA, separate enemy slots, numeric enemy HP/ATK/DEF/AI IDs, and 2022 encyclopedia exact name/element ID comparisons. Identify mismatches rather than equate 2014/2022.
* Provide per-wave summaries and source coverage integrity: 21 missions, 112 waves, 264 archived enemy entries, 42 historical unit IDs, 2,291 2022 Global forms; **zero 2022 native formations verified**.
* No original skill effects were added to the optional training battle; their authentic names and descriptions are research-only until native formulas and hooks can be established.

**Original campaign**: 106 recovered 2022 English quests, 23 dungeons, 3 regions and all previously implemented offline features are preserved. This is still a reconstructed **demo**, not full native Global gameplay, late-world access or restoration of original battle rules.

Security and compatibility: Android package ID and persistent debug signing key unchanged. Existing v7 save and save functions unchanged. The dossier performs no persistent storage or real combat writes. Full Playwright and packaged Android APK regressions required before release. Export the current save first and install in place; physical device testing is still required.
