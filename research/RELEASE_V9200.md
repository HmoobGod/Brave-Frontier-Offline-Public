# Brave Frontier Global v92.00 — Live Original Offensive BB Level Modifiers

**Verified baseline:** v91.00 Build #339, commit `9488ab7e95202e6d64a9e6073c1f8fdee9bd5d86`, signed APK artifact `12597755025`.

## Gameplay restoration
The already verified source archive `source_data/bf_global_original_bb_power_v030.json` records **24 original 2022 Global offensive Brave Bursts**, each with exact Lv1–10 primary damage-modifier percentages from `F_SKILL_LEVEL_MST_{1..4}_Ver1487.json` (240 skill-level values). Previously only Lv1 was used during real demo combat; Lv2–10 were displayed as reference.

`bf9200_source_offensive_bb_levels.js` intercepts the existing global `bbDamageMultiplier` function after all previous modules load and reads the battle-only Lv1–10 selector already provided by v68. A valid original source-supported offensive BB now uses its exact selected original modifier during the existing playable **DEMO** attack; e.g., unit #10011 Flare Ride Lv1 +30% versus Lv10 +75%. Unit #10021 Lv1 +150% versus Lv10 +240%. All other attack calculations and 2022-source-supported targeting remain unchanged.

No new permanent mastery is created: on battle reset the selector returns to Lv1. The original formula for ATK, DEF, spread per hit, REC and other modifiers remains DEMO; only the first source-known primary percent is applied. Skills with additional groups or secondary effects do not receive invented extra effects. When the optional module is absent, when the skill is unsupported, for normal attacks, or during training, the existing Lv1 implementation remains unchanged.

## Safety / verification requirements
- Preserve the complete v91 working inheritance, including original innate 100% ailment immunity, 2022 source BB/normal crystal reference events and all other tests.
- No `P` or `localStorage` writes, no new save fields, no changes to `bf_global_offline_demo_v7` / `P.version=7`; old installs and owned units remain compatible.
- Keep `org.bravefrontier.offline`, same Android development signing keystore, offline manifest without INTERNET permission.
- Browser regressions verify all 240 archived skill-level entries, default Lv1, Lv10 direct and live battle damage changes, invalid/unsupported skills, reset, training behavior, and save isolation. Android packaging regression checks the signed debug APK.
- **Do not promote unless the exact v92 commit passes GitHub Actions and contains an uploaded signed APK.** A green CI result cannot verify physical Android device installation.

## Further native gameplay work
Recover the actual 2022 mission-to-enemy wave join, native enemy AI and combat rewards before replacing existing demo enemies. Recover actual 2022 crystal pickup recipients and BC/HC conversion before adding BB/HP gains. The partial DecompFrontier server/client code does not by itself establish these missing mechanics.
