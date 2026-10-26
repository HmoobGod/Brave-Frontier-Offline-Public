# Brave Frontier Global v27.00 — Source-matched Event Backdrops

Baseline: v26.00 verified original portrait stage (parent expected Build #218). This is an offline, read-only **static scene stage** integrated into the existing three-region original dialogue viewer.

`bf2700_original_event_stage.js` links all 20 supported 2022 Global event scripts' original PARAM id=1 bg1 filename declarations to the exact already-packaged original dungeon JPG assets. These are not inferred via mission ID or copied between dungeons: every pairing was checked against the source event script. The original `dungeon_battle_10200.jpg` was recovered from the user's `BF1_dungeon_part001.zip` (36,820 bytes, SHA-256 50b7833e5045b5ffbf23056d33ee13d1e96654e9665e6b4d770fe6f8baef473b), committed unchanged, and automatically packaged via `prepare_original_event_backdrop_v2700.py`. The unavailable/conflicting `map3-dungeon6.txt` remains excluded. Mission clear messages do not claim an original scene background.

The stage updates when the reader changes scene or advances a dialogue frame. No original face/portrait animations, camera movement, sound triggers or timed scene choreography are asserted. Original cutscene appearance is **partially** recreated only. No autosave, resource grants, changes in combat or Android package/signing/permissions.

Required: browser scene-stage regression, all inherited regressions, assembled Android APK, packaged 20-background integrity test, offline identity and retained v7 save.
