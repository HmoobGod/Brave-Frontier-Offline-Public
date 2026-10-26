# Brave Frontier Global v6.00.0-demo — Original Skill-Level Practice

Baseline: v5.00 Build #173 / commit 5ff1bbe920f3c03237a99477c35b42e8430e7645.

The original 2022 Global decoded skill-master files contain ten documented Brave Burst levels for each of the 24 offensive and 6 support skills already represented in the optional v5.00 tactical sandbox. v6.00 **recovers and exposes all 300 existing Level 1–10 source entries** in read-only reference form, with strict in-game level selection for the six owned/equipped training units.

For an offensive BB, first source modifier and original target scope vary with the selected skill level. For party healing BBs, the recovered low/high range at the selected level is used to generate a midpoint synthetic heal; original REC scaling remains undecoded. For two party-wide ATK skills, their recovered per-level source percentages and duration entries are used in the synthetic battle. Skill-level selection is never saved as true character proficiency.

No gameplay data is fabricated; skill names, IDs, level ranges, source modifiers and first-group effect codes match the existing original Global tables. **This is not full original battle restoration**: charge rates, damage, missing secondary effects, timing, buffs and healing computations remain clearly separated as demonstration behavior. Provenance: F_SKILL_LEVEL_MST Ver1487 archived 2022 tables, original archive SHA-256 69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9.

All source level choices exist only inside volatile tactical practice (undo preserves the selected level at the start of each resolved round). The real campaign, 106 quests, 2,291-form archive, 2014/2022 source separation, native game battle, saved v7 roster and resources are unchanged. Android APK must pass complete browser and packaged regression suite before release.
