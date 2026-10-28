# v139 — Execute independently authenticated 2014 source enemy AI in isolated playable Archive Trials

## External source and fidelity boundary

The source is [cheahjs/bravefrontier_data, Basics of Battle 2014 mission](https://github.com/cheahjs/bravefrontier_data/blob/master/missions_parsed/Basics%20of%20Battle_2014-03-10-20-43.json), Git blob SHA-1 `797a2945a40bcfffe7dfc500c8e3dfb6eb81b8fe`. It explicitly defines one action per turn (`"act counts": "1~1"`) for all four enemy slots across three waves, with a single `attack` action weighted 100%, parameters `-1`, `target conditions="random"`, `target type=2`, empty action conditions. The verified source/slot mapping is Mossy #30030 (wave 1), Sparky #40030 + Mossy #30030 (wave 2), King Mossy #30031 (wave 3). These are authentic **2014 archive records**, not authenticated 2022 Global native behaviors. Independent GitHub source data is used as factual evidence; no third-party implementation code is copied.

## Real functional integration

The existing optional **Archive Trials** mode (`bf200_historical_wave_lab.js`) has an isolated, playable 2014 *Basics of Battle* practice. Its earlier enemy volley was entirely synthetic and did not use the source enemy action records. v139 now constructs a fail-closed, per-living-enemy **source AI action plan** at every enemy reply when mission ID 1 is running. Each source entry must match its archived original 2014 wave/slot, unit ID, name, starting HP, ATK, DEF, AI ID and one-attack-per-turn/100%-weighted `attack` action. The active simulation executes one source-selected attack decision per living enemy, not for KO'd enemies. It records an explicit human-readable original-source AI cadence in the practice log.

**Critical distinction:** The practice still has one synthetic aggregate player HP bar. Original native random player-target selection, hit animations, 2022 enemy AI, actual damage formula, reward and unit drops are **not** implemented or implied. Existing synthetic hit damage uses the same `max(12, ceil(ATK/12))` training arithmetic, Guard the same 30% multiplier. For all missions other than the 2014 *Basics of Battle* reference, and if the source archive is missing/mismatched, the previous synthetic enemy volley remains unchanged. No extra player kills, automatic rewards or original skill mechanics.

## Safety and regression gates

- Exact feature generated script validates under the 64-KiB WebView JavaScript reader.
- Browser regression performs source-based wave 1/2/3 replies, checks the two attacks in wave 2, excludes KO'd enemies, tests missing-source fallback, and compares `P`, live battle `S` and `localStorage('bf_global_offline_demo_v7')` before/after the entire practice. **No owner save mutation or playable units unlocked.**
- Signed APK regression checks the packaged historical source action planner, source identity, existing historic module and unchanged v7 key.
- v139 source patch is limited to the already-shipped Archive Trials practice, not 2022 storyline quest encounters. No Android signing, app package, gameplay HP/BB AI, quests, currency, EXP or material inventory change.
- Faithful 2022 NPC AI would still require an actual 2022 mission-enemy payload and native targeting/packet evidence. Do not silently substitute 2014 evidence for 2022.

CI gate: exact v139 feature branch SUCCESS, then merge only onto the newly verified main head; fresh main build must succeed before declaring stable. Owner installed v124, next requested APK around v150.
