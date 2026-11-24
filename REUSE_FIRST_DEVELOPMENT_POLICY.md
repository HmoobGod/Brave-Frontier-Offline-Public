# Brave Frontier Global Offline — Reuse-First, No Unnecessary Rebuilds

**Owner decision recorded:** 2026-11-23 (America/Chicago)  
**Applies to:** Home-first reconstruction and subsequent Brave Frontier development  
**Authority:** Owner's explicit project direction. This is a development policy, not source authenticity, asset-license, merge, or APK-release approval.

## Decision

**Reuse verified original resources and retain working systems. Do not rebuild Brave Frontier or its Home screen from scratch merely because the visual presentation is incomplete.** Replace or improve individual components incrementally. A large redesign or architecture replacement requires concrete evidence that the existing system cannot meet a necessary requirement and separate owner authorization.

## Working rules

1. **Search existing material first.** Before creating art, UI components, animations, or renderers, check our own source archives, staged assets, manifests, existing code, prior research, and relevant public preservation/reconstruction repositories. Do not repeat already-settled discovery without a new reason.
2. **Prefer authentic, verified resources.** Record exact source URL/path/commit, file identity (SHA-256 or Git blob where applicable), edition and date provenance, expected dimensions, and any transformations. Distinguish original Global client data from 2014, EU, Japanese, Reborn, fan-made, or other revisions. Repository availability alone does not grant redistribution rights.
3. **Copy assets only after verification and reuse clearance.** A PNG can be added directly as an asset if correct, available, hash-checked, and permitted. Animations may require translation/rendering of CGG/CGS/SAM metadata. Godot/Unity/Cocos code is not directly compatible with our Android WebView HTML/CSS/JS client; translate documented behavior or use appropriately licensed implementations.
4. **Preserve functioning systems.** Keep our existing navigation, playable Quest, Units, Summon, Menu, owned six-unit 3×2 custom Home, leader slot one, accessible full names, visible Quest, fixed footer, save/progression/economy, and tested phone compatibility. Do not revert to the original five-slot layout or introduce fictional 2022 content.
5. **Implement in small, isolated cycles.** Prototype source-only with actual verified art and responsive Chromium evidence (320×740, 393×852, and short heights) before proposing an APK. Keep code size limits and module-loading contracts in view. Use Claude for targeted implementation when useful; ChatGPT can research and independently review.
6. **No restart by default.** Consider a broader rebuild only with a written limitation, failed alternatives, migration/rollback plan, independent review, and explicit owner approval.
7. **Protect all release gates.** Draft PRs, protected main, exact-head review, signed Android CI, owner-device acceptance, installed APK and private canonical v7 saves must stay distinct. Never promote by source tests alone. Preserve `org.bravefrontier.offline`, no `INTERNET` permission, player-only Auto/manual fallback, unchanged enemy/NPC AI and no automatic item/capture. No unsanctioned merges, APK builds/installs/releases, protected-file access or schedules. Keep Issue #614 **BLOCKED** until actual owner Home acceptance; original April 2022 authentic formations remain **0/106** until independently evidenced.

## Source reuse leads established in v643–v644 research

- **Original client Home references:** [Seltraeh/Brave-Frontier-Offline](https://github.com/Seltraeh/Brave-Frontier-Offline), including `assets/layout_home2.csv`, `sg_PortraitDimension.csv`, `MypageAura1–6.sam`, `LeaderMark4.sam`, effect layers and `attribute_mark.png`. Original-client origin needs edition/date verification; copyright/reuse permission is separate.
- **Six starter full illustrations and battle sprite sheets:** [MastroCaleb/BF-Legacy](https://github.com/MastroCaleb/BF-Legacy), `Assets/BF_Assets/content/unit/img/`, names `unit_ills_full_{10011,20011,30011,40011,50011,60011}.png` and `unit_anime_*.png`. Git LFS pointers provide SHA-256 identities, but pointer files are not image bytes. Full art for first four base starters also directly readable in Seltraeh; Magress/Atro full PNGs require fetching/verifying referenced LFS objects.
- **CGG/CGS base-unit animation geometry:** BF-Legacy `Assets/BF_Assets/content/unit/cgg/unit_cgg_<id>.csv` and `cgs/unit_idle_cgs_<id>.csv` found for all six starter IDs.
- **Cross-reference:** [aMytho/brave-frontier-godot](https://github.com/aMytho/brave-frontier-godot) has a Home scene and six element-glow image sets; 24 layers byte-identical by Git blob to Seltraeh's original-client MypageAura layers, but Godot scene placement/timing remains fan reconstruction.
- **Animation implementation reference:** [BluuArc/BFFrameAnimator-js](https://github.com/BluuArc/BFFrameAnimator-js), MIT-licensed JavaScript code for original CGG/CGS data; its code license does not license original game art.
- **Artwork discovery lead:** [Nervequakes/BF-Companion](https://github.com/Nervequakes/BF-Companion), an offline unit guide claiming original art and idle sprite resources for 2,292 units; inventory/revision and redistribution rights need separate checks.

## Current checkpoint (not a release decision)

- Protected `main`: `d21f069a43351aaf78374d46448f9dd0756a8457` at documentation authoring.
- Home PR [#637](https://github.com/HmoobGod/Brave-Frontier-Offline-Public/pull/637): draft/unmerged, last verified head `586b9214cec2b346aef9c7a409ae9f8fd7a8c840` and base `2a03c95d0371b9319e1799d994e2ea25ac6341f2`; Build #2654 CI passed, but visual owner acceptance remains open.
- **Next visual step:** obtain verified and permitted actual original base-starter images, isolate source-only art composition, then compare mobile snapshots before any build/release action.
- Authoritative [Brave Frontier — MASTER DEVELOPMENT STATUS](https://docs.google.com/document/d/1M2XfkoNH-0Fy9gFrYAskmUBMMZg3fOj-Gz7SNYwN9M8/edit) tracks ongoing state. Reverify live head, CI and owner-installed build before acting.

**This file is documentation only. It does not authorize staging assets, changing gameplay, modifying PR #637, merging, building or releasing.**
