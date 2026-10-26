# Brave Frontier Global Offline — v102.00 Unit Favorites and Lock Markers

Parent: v101 isolated original dialogue skip development candidate. Not a verified main release until CI passes.

- Optional per-owned-base-unit Favorite and Lock flags in existing Unit Box. Indicators are displayed on Unit Box cards and controls for the currently selected unit.
- Stored separately in app-local preferences (bf_global_offline_qol_unit_flags_v102). Never adds any fields to P or v7 game-save JSON.
- Flags can be toggled only for currently owned base IDs. Imported saves that lack the unit will not display the marker, but local markers are retained in case the unit returns.
- The current game has no native selling/fusion UI. Lock flags are clearly **advisory** until those mechanics are implemented and explicitly checked against these flags. No false protective guarantee.
- Existing quests, combat, summons, saving, and evolution continue without modification. Browser and APK regressions required.
