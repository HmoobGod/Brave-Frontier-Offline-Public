# Brave Frontier Global — v1.50.0-demo release engineering

## Proven baseline
Parent: v1.20 Build #159 / commit d35bcf0b456a5b6f8680aef2f90de5d4e81ca0a5.
Leave all 106 source-backed quests, 23 dungeons, three Grand Gaia world maps,
source-era research, playable DEMO combat, signed Android application ID and
save schema bf_global_offline_demo_v7 unchanged.

## Added: research + gameplay-adjacent QA

* **v1.30 scope**: Cross-reference the **distinct historical 2014 enemy unit IDs**
  in four known missions against the checked-in 2022 Global unit encyclopedia.
  Report only exact ID presence and separately normalized English-name matches.
  This is not proof of a 2022 encounter, drop table or AI mapping.
* **v1.40 scope**: Offer read-only wave-by-wave enemy scouting panels for four
  historical missions, with original **2022 unit thumbnails only where the
  original encyclopedia declares them available**. No thumbnails are
  asserted to reproduce historical battle animations.
* **v1.50 scope**: In-game offline integrity readout of 106 distinct quests,
  23 source dungeons, 34/36/36 regional counts, 2,291 original archive unit
  forms, and four research records (16 groups / 33 entries). Status uses
  in-memory data; no network calls, new saves or combat mutations.

The original 2022 enemy wave formulas, 2022-native enemy spawning, AI, drop
rates, and damage rules **are NOT restored or claimed**. No research-only
records can change a player's units, missions, battle or rewards.

## Acceptance rules
GitHub Actions must pass both full historical browser regressions and
the new cross-era read-only QA + APK checks, including no app INTERNET
permission, unchanged app ID, debug signing key, existing save v7 schema,
and source/presentation boundary. Android on-device testing remains a
separate, unfulfilled acceptance step until the user runs the APK.

For in-place installation export a backup first and never clear old app
storage or replace the signing certificate. Official live Global service
and multiplayer are not part of this purely offline reconstruction.
