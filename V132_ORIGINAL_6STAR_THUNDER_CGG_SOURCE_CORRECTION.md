# v132 — 2022 Global six-star Thunder source-opacity and horizontal-flip correction

This is a **visual fidelity correction for an already-playable unit**, not an extra unit or combat mechanic. The owner's original 2022 Global CGG/CGS and sprite sheets are preserved; neither saved progress nor APK signing changes.

The specific 6★ Thunder alternate **#40025** has 27 CGG composition frames and 232 layers. Only three original CGG layers require a non-default transform: frame 6 layer 6 has 50% opacity, frame 15 layer 1 has a horizontal flip (code 1), and frame 24 layer 0 has 50% opacity. All its other CGG layers have source flip 0, blend 0, opacity 100, rotation 0 and sheet page 0. Independent [BluuArc BFFrameAnimator](https://github.com/BluuArc/BFFrameAnimator/blob/master/src/Frame.java) community reverse-engineering supplies field interpretation; this is not proof of exact 2022 mobile blend and clipping implementation. No code has been copied from that project.

Previous original v38 image generator incorrectly treated the two source opacity values as sprite resize percentages and entirely ignored the horizontal flip. v132 changes **only** #40025 by applying source half-opacity to the raw cropped pixels and mirroring the one part. All other 71 playable units, CGS sequences, source pixels and assets are unchanged.

Prior v124 packaged image SHA256 **54a3adb6dafe3fd52a6797223b12354f1d8ce403972e92e69fd6af614f773c07** reproduced byte-for-byte. New source-derived PNG SHA256 **7273c43cead5d10c1ba47b59888379a808411c3ed7a3fa1894a277e970ccc90b** checked by an independent second rasterization and signed APK test. The v131 6★ Earth correction #30025 remains byte-identical. Four other 6★ alternate atlas checksums remain unchanged; all original archive/test/regression source material persists.

`test_bf_original_sixstar_thunder_v13200.py` independently reconstructs all 232 layers, checks the three source transform positions and five other original six-star atlas SHA256 digests. `test_bf_packaged_6star_thunder_v13200.py` checks the Android APK embeds the exact new PNG and contains the unchanged `bf_global_offline_demo_v7` save key. Previous v131 regression is consciously updated to expect #40025 new SHA.

No 7★/8★ playable expansion is implied. Preserve v7 save and original source, leave unsupported CGG rotations and blend rules untouched. Merge only after exact v132 feature-head CI SUCCESS and v131 fresh merged-main CI SUCCESS; verify a fresh merged-main success before declaring v132 stable. User installed v124 until v150.
