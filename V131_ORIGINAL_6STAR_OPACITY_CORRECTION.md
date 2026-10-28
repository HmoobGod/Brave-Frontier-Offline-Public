# v131 — Source-corrected original 2022 Global 6★ Earth alternate sprite

This is a **live playable artwork correction**, not a read-only archive entry. No new unit is recruited, no gameplay formula is modified and save version 7 is unchanged.

Original source: owner's `BF1_unit_part001.zip` SHA256 `c0f03306a4e5efd2513c982ac58b12fff2d72c9ff978b19a839f8932536fc846`; the corresponding six-alternate pack is already pinned in `source_data/bf_global_other_six_star_v038.json` / `source_assets/bf1/BF1_Global_2022_Other_Six_Star.zip.b64`. Independent [BluuArc BFFrameAnimator](https://github.com/BluuArc/BFFrameAnimator/blob/master/src/Frame.java) decodes original CGG column 4 as **opacity percentage**, not sprite scale. This community implementation is source-level evidence, not proof of the 2022 Global native code.

The 6★ Earth alternate **#30025** is an ideal scoped test: its original CGG contains 23 frames / 264 layers; **only six layers in frame 19** have opacity `50` rather than `100`. Every frame's source flip, blend and rotation is `0` and uses sprite-sheet page `0`. Thus the only transform change needed is original-frame alpha 50%, **not resizing six parts by 50%** as the v38 generator did. All source positions, geometry, PNG pixels, CGS sequences, animation speeds and 71 other playable forms are unchanged.

With original atlas layout 2400×2000, Pillow PNG source-base build from v38 reproduces the current APK's previous target SHA256 `fb7c5d78417740e862c2c42de70a430efec0698f6e8000a04d1a3a0ba62f733e`, while alpha-aware source rebuild yields SHA256 `53295c806e6390e05a74e7ed124e709e9c677753070fc44eb1e3c262131623b5` (strictly one target). The v131 tests independently check source raw CGG values, six alpha transformations, exact rendered target SHA, exact unchanged hashes of the five other original alternate 6★ atlases, signed APK packaging, 72 forms, and saved `bf_global_offline_demo_v7` state.

Do not apply the same change universally without proving other forms' flip/blend/rotation semantics and reviewing final artwork. Correcting #30025 provides a safe, source-verifiable first step toward source fidelity for 6★ artwork. This replaces no original native renderer and does not alter combat damage, AI, rewards, EXP, items, evolution costs or source assets.

Merge only after exact v131 feature CI SUCCESS and v130 merged-main CI SUCCESS. Then verify fresh merged-main CI. User installed on v124; next planned APK v150.
