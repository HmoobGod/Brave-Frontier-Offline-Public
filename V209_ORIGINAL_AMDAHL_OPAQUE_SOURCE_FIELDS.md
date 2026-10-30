# v209 — Original 2022 Amdahl source fields, read-only

**No battles unlocked, no new enemies, AI, drops, audio playback, material
rewards, original Gem awards or saves changed.**

The v206 original Amdahl Story Guide shows all 36 source-backed original 2022
quests, but does not expose four other original mission-master fields or
its `npcId`. Rather than inventing their meanings, v209 adds a collapsed
*raw source fields* pane under the existing v206 guide.

Every mission now has a read-only source row showing:
- The `rawEncounterRef` string (opaque group references, **not** a decoded
  battle lineup or a drop percentage).
- The original `battleMusic` and `bossMusic` **file names only**; audio
  is never loaded or played.
- The original `rawRewards` token, including the seven Amdahl end-quests
  with `8:0:1:0:0`. This is **uninterpreted archival text**, not a drop,
  reward value or eligibility to claim an item.
  **For Amdahl, the token is shown only as an uninterpreted original string;
  no first-clear reward or other payout is applied.** This is distinct from
  the project's custom first-clear Gem handling for already-playable quests.
- The original `npcId` (all zero for these 36 source rows). This is not
  a playable NPC or a recovered NPC AI script.

## Evidence and safety boundaries

Source file: `source_data/bf_global_2022_amdahl_quest_readiness_v147.json`
(the authenticated 2022 mission master and archived English quest joins).

- Original translated mission master SHA-256:
  `d4e364b6c1c5a825c0153c57bdd4123cd35800c74db795d913d119b6c9a99f83`.
- Original v147 36 quest canonical SHA:
  `f35a7b06bc9e6fae6facc1fd77422f74c04798da4fb87f64a2737a0483a572c3`.
- Exactly seven original dungeons / 36 original missions. The existing
  106 playable quests remain unchanged.
- Before creating the pane, the script checks v206's original guide,
  master/canonical digests, v151's source-only encounter ledger, each of the
  36 original 2022 opaque encounter strings and NPC/source record shapes.
  No new game actions or save writes are present.
- Text is written with DOM `textContent` only, never interpolated HTML;
  `MutationObserver` tracks the existing v206 dungeon selection/map pins
  without changing v206's click handlers or save state.
- The module is loaded separately and optionally by `MainActivity`
  **after v206 and before v174**, with a warning if the optional APK
  asset is missing.

## Tests / merge gates

`test_bf_amdahl_original_opaque_metadata_v20900.py` compares **every
one** of the 36 packaged JS tuples to the source fixture on all six
fields, checks 7 dungeons and the 6-mission final dungeon using actual
prepared 106-quest HTML with the original v149/v151/v206/v209/v174
modules, confirms the raw music/reward tokens, verifies fail-closed
behavior on incompatible player version and corrupted source metadata,
and compares v7 player, quest list and save storage before and after.

This modifies the **user-visible Android WebView script chain**, so it
requires exact-head green full Android CI **and independent Claude
review** before PR merge. Do not call this restoration of original
enemy encounters or guaranteed Android device compatibility; a real
owner-device save smoke is still required.
