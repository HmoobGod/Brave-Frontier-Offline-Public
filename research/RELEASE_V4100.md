# v41.00 — Optional Original Quest Name Inside Active Battle

Baseline: v40.00 original-next-chapter-intro patch, pending Android verification.

Adds an **off-by-default** checkbox in the live story HUD: **OPTIONAL MISSION NAME IN BATTLE**. When enabled for any of the 106 supported archived 2022 Global quests, a compact, touch-transparent badge is layered over the existing playable demo battlefield with the source-recorded mission title, source dungeon name and currently simulated wave position. This improves contextual continuity between original cutscene introductions and live demo encounters.

Training mode and unsupported/locked missions hide the badge; the option only lives for the current UI session and never changes the actual stage sprites, enemy formations, original source dialogue, AI, target selection, game progression, rewards or saved settings. Current waves and victory/defeat flags are explicitly DEMO while recovered quest names are original archive metadata.

The Android package ID, debug signing key, offline permissions, v7 save schema and local save key remain unchanged. Browser tests cover on/off, training isolation, source quest title, no save/turn mutation and integrated dependency injection. The signed APK is separately checked for the new optional script.
