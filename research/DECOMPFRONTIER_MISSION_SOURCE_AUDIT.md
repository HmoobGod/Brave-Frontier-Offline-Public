# DecompFrontier and historical Global mission audit (2026-10-25)

## Existing implementation must not be duplicated
Before this audit, v1.20 already preserved four archived 2014 missions including **Basics of Battle**, and v2.00 extended these to **21 2014 missions / 112 waves / 264 enemy slots / 42 distinct unit IDs**. The v1.50 module cross-matches numeric unit IDs with the 2022 encyclopedia. These are optional, separate research and synthetic practice; they are not confirmed 2022 encounters.

## Sources and licensed-code boundary
- DecompFrontier documentation: https://decompfrontier.github.io/ (architecture/research).
- Decompiled client: https://github.com/decompfrontier/client (incomplete native C++ client).
- Server: https://github.com/decompfrontier/server (AGPL-3.0, incomplete handlers, not integrated).
- MST/packet generator: https://github.com/decompfrontier/packet-generator (MPL-2.0, schema investigation only).
- Scripts: https://github.com/decompfrontier/scripts (MIT scripts, no code copied).
- Original older archive: https://github.com/cheahjs/bravefrontier_data ; `missions_parsed/Basics of Battle_2014-03-10-20-43.json`, Git blob SHA-1 `797a2945a40bcfffe7dfc500c8e3dfb6eb81b8fe`. This Git blob hash was verified against that exact public GitHub file. Archive is historical; do not infer repository-wide licenses where none were established.

DecompFrontier server's `MissionStart.cpp`, `DeckEdit.cpp`, `GatchaList.cpp` are documented as Unsupported in the previous authenticated handoff. Do not integrate a remote service or copy AGPL source into the private Android app. Public sources were examined as research only; all v87 JavaScript code is independently authored.

## Historical Basics of Battle exact parsed fields (2014)
The original parsed archive has three waves and four enemy slots:
- Wave 1: Mossy #30030, earth, HP 300 / ATK 290 / DEF 50.
- Wave 2: Sparky #40030, thunder, HP 300 / ATK 320 / DEF 0; Mossy #30030, earth, HP 300 / ATK 290 / DEF 50.
- Wave 3: King Mossy #30031, earth, HP 3000 / ATK 320 / DEF 30.

Each archive enemy has AI ID 1 with one action per turn (`act counts="1~1"`), a 100%-listed `attack` action, parameter `-1`, `target conditions="random"`, target type 2, and an empty action condition list. Each has listed curse/injury/paralysis/poison/sick/weaken resistance **0%**. All four have Zel drop count 5 and Karma drop count 5. The maximum per-drop Zel/Karma archive values are **12/8** for Mossy and Sparky, and **120/75** for King Mossy. The first Mossy and Sparky have archived unit drops at level 1, 100%, type random. Second-wave Mossy has a treasure record: chest 100%, Zel 500 at 50%, Karma 250 at 50%. Other item-drop lists are empty. These are **source record values, not validated runtime output rates**.

## Confidence / interpretation
- `RECONSTRUCTED_FROM_ARCHIVE`: exact historical mission names, wave slots, raw stats, AI action labels/weights, resistance fields, and listed drop record fields.
- `ORIGINAL_SOURCE`: repo's 2022 Global `F_MISSION_MST_1_Ver1118.json` and archive unit masters exist but the original 2022 native mission enemy payload is **not decoded**.
- `UNVERIFIED`: 2014-to-2022 match of formations, native random-target implementation, AI scheduler, drop probabilities, chest calculation, enemy rewards and native damage.
- `DEMO_FALLBACK`: existing 2022 WebView battles and standalone v2.00 practice keep their prior synthetic mechanics, without being relabeled as original.

The English title/mission ID association in the existing 106-quest catalog is not an exact 2022 enemy-wave proof. No 2022 formations, enemy AI, or item/reward grants were promoted by v87.

## Engineering contract
New module `bf8700_original_basics_ai_reference.js` is source-gated against the already shipped v1.20 and v2.00 mission records; exposes only immutable inspection, and adds an expandable UI to the optional historical Archive Trials panel. It does not execute the archived AI, mutate saves, alter fights, request a network endpoint or assign rewards. No new Android permissions, files needed from user, asset downloads or signing changes.

Next original-playable integration gate: identify and hash a **2022 Global mission-to-wave payload**, prove the exact enemy ID/slot/AI schema and reward values, then independently implement one deterministic encounter behind a safe source-verified fallback. DecompFrontier MST schemas may help identify original fields, but names alone are insufficient.


## 2022 early-mission field countercheck (October 25, 2026)
The untouched archived `3-mst-translated/F_MISSION_MST_1_Ver1118.json` file (SHA-256 `d4e364b6c1c5a825c0153c57bdd4123cd35800c74db795d913d119b6c9a99f83`) contains **35 recorded missions with integer IDs 1–106**. These 35 mission rows have **nine different** values of the untranslated field `MISSION_8f4NYKxb`. The string `3:10100,1:10101,0:10102` repeats for mission IDs **1, 2, 10, 11, 12**, although their official `missionBattleCount` values vary across **3, 5 and 6**. It therefore **does not supply a self-evident per-wave encounter list**; mapping its numeric codes directly to encounter enemy IDs would be an unsupported guess.

Other groups repeat by local area or dungeon and also have variable battle counts (for instance `3:10200,1:10201,0:10202` for missions 20–23 with 5–6 recorded battles). Source strings and mission rows can be used as immutable original provenance, but the true meaning of the opaque field remains **UNDECODED**. Before using it in playable encounters, obtain an independent field definition or native scene/packet trace that associates mission IDs with wave enemy IDs, positions and AI, then cross-check the 2022 data. No original 2022 waves or enemy AI can be promoted on this field alone.
