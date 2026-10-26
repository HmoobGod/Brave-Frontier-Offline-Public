# v34.00 — Original Event Character Source Coordinates

Baseline: staged v33.00 optional source dialogue auto-player. Promote only after exact-source CI.

The immutable `BF1_event_part001.zip` contains 405 original MSGDRAW frames across 20 supported 2022 Global dungeon scripts. `PARAM id=2` specifies a sprite reference and X/Y placement whenever each character image is changed. Parsing the source scripts and carrying forward coordinates across successive MSGDRAW frames shows these pairs consistently across all supported frames: **Tilith (+60,+30)**, **Karl (-110,-40)**, **Seria (-50,+20)**. The source expression and speaker map from v29/v28 already select the correct character per line.

This optional presentation now positions the static original portrait on the left or right of its dialogue within the responsive mobile reader using the original sign of X, and shows source X/Y numbers. **Do not confuse this with native pixel coordinates**: the renderer's original coordinate transformation, motion ease, timing and stage dimensions are not recovered. The implementation explicitly labels its placement as approximate.

No game progression writes, quest bypass, combat changes or networking. Browser regression tests the source coordinates and reader's actual Karl→Seria transition; package regression checks offline APK and preserved v7 save.
