# Brave Frontier Global Offline — v101.00 Viewed Dialogue QoL

Base: v100 feature candidate, no release or main promotion yet.

- Track a source-verified archive dialogue scene only after its final page has been viewed.
- Local record is bounded to 40 scenes under separate key bf_global_offline_qol_viewed_scenes_v101.
- Quick skip is disabled for scenes not previously viewed; when enabled calls existing unlock-gated timeline navigation.
- No automatic quest/dialogue progression, scene unlocking, script change, save migration, or alteration to original v7 save.
- Tested in a simulated Chromium dialogue reader; Android device verification remains outstanding.
- Scenes viewed before this QoL release are not inferred retrospectively; reach the final page once after installing.
