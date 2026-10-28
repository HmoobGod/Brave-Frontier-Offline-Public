# v146 — Source-correct 2022 Global 5★ Death Magress sprite animation

This patch corrects **one already-playable original Global unit's battle artwork**, not unit stats, skills, summoning, evolution or AI. The owner-provided original 2022 Global `BF1_unit_part001.zip` and exact v0.35 source pack contain `unit_anime_60014.png` and `unit_cgg_60014.csv`. The original 5★ Dark starter **Death Magress #60014** has 30 CGG sprite frames / **251 layers**.

An independent [BFFrameAnimator](https://github.com/BluuArc/BFFrameAnimator/blob/master/src/Frame.java) community interpretation decodes CGG field `orientation=2` as a vertical flip and the `scale`-named original fifth field as **opacity percentage**, not sprite resizing. For this precise form every source CGG blend, rotation, source-sheet page and reserved flag is zero; other forms with complex fields remain unchanged. This is not a claim to reproduce the complete 2022 native animation renderer or its timing.

The v0.35 generator previously **ignored eight original vertical flips** and **resized** patches where the source specified eighteen opacity percentages (30%, 40%, 60%, 80%). Some patches require both transforms; exactly **22 unique source layers** change. All crop positions, frame order, source pixels and CGS motion sequence are retained. Five other 5★ starter atlases stay byte-identical.

Using the exact original 2022 source assets, an independent Pillow rasterization reproduced the **installed v124 APK's existing 60014 atlas byte-for-byte**: SHA256 `3301ac9b3bb828ed31d3146a128833602013ef0a236a6a6709e0f90b14548b0d`. The single corrected atlas is SHA256 **`e8582ed0a8a1eba005b208def14d97ba8f2892d38c83629941b536c2ac7b2b46`**.

The independent test `test_bf_original_dark_five_star_source_art_v14600.py` checks the exact original pack and six source-file hashes, all 251 source CGG layers, 8 flip source positions and 18 original opacity source values, independently rebuilds both old and corrected atlas pixels, and confirms the other five source sprite atlases and unchanged v7 save key. `test_bf_packaged_dark_five_star_source_art_v14600.py` checks the new signed Android APK embeds exact corrected PNG and all other five unchanged image SHA256 digests.

### Scope / safety

- Changes the image-generation treatment of **only unit #60014**, in `prepare_original_five_star_starters.py`; leaves five other 5★ starter forms unchanged.
- **No new playable 7★/8★ units**, native damage/target RNG, altered BB, UI navigation, game currency, quests, enemy AI, source master values, saved EXP, evolutions, player roster or Android signing changes.
- `P.version===7` and save key `bf_global_offline_demo_v7` retained; no migration.
- Source files remain the owner's original trusted and hashed bytes.

### Promotion

Branch `feature/v146-original-dark-five-star-source-opacity-flips` starts on exact v145 feature-head commit `b1019eac57ad23df291847b9021596a6f440a714`. **Do not merge** until PRs #56–#60 (v141–v145) are each proven by exact feature CI and merged-main CI, in dependency order. Then require **exact v146 feature-head GitHub Actions SUCCESS** and fresh postmerge main SUCCESS. Owner remains on installed v124 until requested v150 APK.
