# v145 — Source-verified 2022 Global quest music controls (optional)

This is an actual **offline audio gameplay improvement** using three original Global MP3s **already present in the owner's installed v124 APK**. It does not upload or redistribute 15 previously unbundled original copyrighted music files to the owner's public GitHub project.

## Provenance

The owner-provided original 2022 Global decoded MST `mst-decoded.zip` (SHA256 `69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9`) contains 106 currently playable quest rows with exact `missionBattleMusic` and `missionBossBattleMusic` fields. The original owner `BF1_sound_part001.zip` (SHA256 `9be425acdd37d036c2c14b1fa4457aa07632e528e4633d0f9e35b78c4df0be5d`) contains all 18 unique referenced MP3s. These source data are joined to the installed signed **v124** APK's exact quest ID catalog (106/106) and music files. All three existing APK MP3s are byte-identical to the owner's original sound archive.

The packaged source cues include 18 historically named tracks (16 map, 2 boss); only **3 tracks are already included in v124 APK**: `bf010_map_grass.mp3` (5 quest maps), `bf011_map_firecave.mp3` (9 quest maps), and `bf006_btl_boss.mp3` (104 quest boss references). The other 15 cues are retained as source evidence, but no audio playback is attempted for files absent from the APK. No network access or substitute song is used.

## Functional scope

`app/src/main/assets/bf14500_original_global_music.js` introduces a small opt-in **Original Music** panel near the current archived quest details. The user must explicitly press `Play map` or `Play boss`; this is an optional manual choice and **not** a claim that authentic 2022 original transition timing or last-wave boss detection has been reverse engineered. When the original selected source cue MP3 exists in the APK, the button plays that exact original file on loop using ordinary WebView HTML5 Audio. `Stop` pauses and unloads, app background visibility stops playback, and training battles cannot use original quest music; unbundled source music is shown as unavailable and never requested. No automatic playback is enabled. All audio state is session-only and **no save setting is created**.

Exactly **106/106** source quest cue rows are packaged in immutable JavaScript. The original source tuple hash, original asset archive provenance, SHA256s of the three original MP3s, and signed APK payloads are guarded in `test_bf_original_quest_music_v14500.py` and `test_bf_packaged_quest_music_v14500.py`. Browser tests simulate user play/stop, map/boss/manual source changes, unavailable music, training mode and app state preservation, asserting `P`, live battle `S`, and localStorage `bf_global_offline_demo_v7` remain identical.

**Limitations:** We have not authenticated the original client music cues' start/stop rules, or the native battle-map/boss switch point. This new panel is a transparent, user-triggered optional sound player using authentic source audio bytes. No 7★/8★ playability, original 2022 wave AI, XP, loot, intro animation, stamina, title screen or Android permissions change.

**CI and merge:** v145 branch is based on v143 (which in turn includes v142), with independent per-asset tests. Require exact v145 feature HEAD CI SUCCESS and earlier v139–v144 merges with fresh successful main builds; rebase/merge safely on the newest verified main and verify a new main run after the merge. No APK update request to the owner before v150.
