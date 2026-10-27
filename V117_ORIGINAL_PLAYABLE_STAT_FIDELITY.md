# v117 — Generated APK Playable Unit Stat Fidelity Gate

The original 2022 F_UNIT_MST base stat evidence was recovered in v116. This regression-only checkpoint checks the **actual generated game catalog** (after the source asset preparers) against each of those 72 archived unit forms.

Checks:
- All 72 original 2022 unit IDs exist as live playable `UNIT_BY_ID` records in the assembled game.
- All **288** HP/ATK/DEF/REC level-one values match the authenticated 2022 unit master exactly.
- The loaded units preserve each original unit ID and provide a non-empty display name; localized names need not be unique.
- Existing v7 player/save state is untouched by the source audit.
- Existing v115 battle-time max level caps and v111/v113 leader skills remain unchanged.

This is a release-quality data integrity gate, not a claim that the currently DEMO mid-level stat growth or original type RNG is reconstructed. If it fails, correct specific master-to-playable mapping discrepancies rather than weakening the assertion or inventing substitute data. GitHub Actions build/packaging and all earlier Android signing checks remain mandatory.
