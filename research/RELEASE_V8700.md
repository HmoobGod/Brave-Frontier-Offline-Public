# Brave Frontier Global v87.00 — Historical Basics AI evidence (2014, read only)

**Parent:** v86.00 Build #323, verified commit `182dc07c7f6c4f4525a1f066598aa1a04c589b55`, artifact `12590432512`. v87 must independently pass CI and produce a signed APK artifact before promotion.

New `BFHistoricalBasicsAIReferenceV8700` records the exact archived 2014 *Basics of Battle* four enemy slots with action count, AI ID 1, attack chance 100%, random-target descriptor (native RNG deliberately **not** implemented), resistance fields, item/unit/chest records, and Zel/Karma maxima. A read-only inspector appears inside the existing optional 2014 Archive Trials when Basics of Battle is selected. The source is `cheahjs/bravefrontier_data/missions_parsed/Basics of Battle_2014-03-10-20-43.json`, Git blob `797a2945a40bcfffe7dfc500c8e3dfb6eb81b8fe`.

**Explicitly not restored:** 2022 native wave equivalence, native damage or hit scheduling, AI execution, target RNG, item/unit drop calculation, quest rewards, story combat replacement, crystal allocation, BB gauge or HC pickups. The new reference is fail-closed if the existing v1.20/v2.00 identity/stat checks disagree. No save mutations, network runtime access or signing/Android permission changes.

Preserve `P.version===7` and key `bf_global_offline_demo_v7`; full inherited browser and signed-APK packaging tests remain required. See `DECOMPFRONTIER_MISSION_SOURCE_AUDIT.md` for source separation, licensing notes and the 2022 original-gameplay integration gate.
