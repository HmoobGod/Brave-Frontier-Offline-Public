# v133 — Original 2022 Global playable 4★ sprite vertical flips

This revision repairs **existing playable unit artwork** for three original 2022 Global 4★ forms: Water #20023, Earth #30023 and Light #50023. The owner's original Global sprite/CGG/CGS files are source-hashed by `source_data/bf_global_more_second_stage_v034.json` and archived under `source_assets/bf1/BF1_Global_2022_More_Second_Stage.zip.b64`. All original unit identities, attack animation sequences, sprites, recipes and save values remain unchanged.

Independent 2016 [BluuArc BFFrameAnimator](https://github.com/BluuArc/BFFrameAnimator/blob/master/src/Frame.java) interprets CGG orientation code **2 as vertical flip**, not rotation. On these precise three 4★ forms, all other original flags have blend 0, opacity 100%, rotation 0 and sprite-sheet page 0. Source flip rows:
- #20023: source frame/layer (6,2), (7,2), (9,0), (10,0), four vertical flips.
- #30023: (7,0), (8,0), (9,1), (11,1), four vertical flips.
- #50023: (9,0), (10,0), two vertical flips.

The old v34 generator ignored these exact vertical flips. A separate Pillow source rasterizer reproduced all old v124 APK atlases byte-for-byte, then implemented exact source mirroring, preserving all positions and 4★ base art. New source-derived PNG SHA256 values:
- #20023 old `392cb6a8a89f50b29bf3ead1ae154e118df13dff2ab280edf66560d025a8b619` → new `5982e1ed6d9011fbdb79f0882a6385b29b61a24a605ec1442f14ed564f07b07e`
- #30023 old `75f2e25cc127ea4585f0dbe32f0067f83080eeb7cfff9898fea7b5b126fbb63d` → new `fe75fceff32d3357c9aecf078248ce78033c60de72ba853419c00b08f0fc0c46`
- #50023 old `7eec053bf05f90eca64b4776743655162389f47af2c370b935ded4008ff66d82` → new `daf0a9eff2edc1d44602f041d7ae4f0ae4ca7db940d362dcb382155c61e97a46`.

The source generator changes only these three form IDs. All other existing 4★ source art is independently checked unchanged, while the v131 Earth 6★ and v132 Thunder 6★ corrections remain intact. Original combat/BB mechanics, unit stats, quests, enemy AI, EXP, unit evolution, drops, original 2022 source masters and saved v7 player progress **do not change**.

`test_bf_original_fourstar_vertical_flip_v13300.py` reconstructs and hashes exact old/new source art for all three IDs, checks ten source flip positions and all three unchanged companion atlases, verifies no save schema changes. `test_bf_packaged_fourstar_vertical_flip_v13300.py` gates the signed APK's three PNG bytes and v7 save key.

**Authenticity limitation:** These transformations follow a 2016 independent community implementation of CGG, not a reproduced/native-2022 graphics pipeline. No new playable unit count or experimental rendering is implied.

Branch is stacked on exact v132 feature SHA `cd0ae06580ca648c52c61a4757d02544c72ca79a`; do not merge this branch until v132 passes exact HEAD CI and fresh main CI. After v132 merge, retarget v133 onto main, confirm exact feature-head CI success and fresh main CI success. Owner installed v124 and next desired APK update v150.
