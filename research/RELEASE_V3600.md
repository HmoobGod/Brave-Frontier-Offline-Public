# v36.00 — Unified Original Event Scene Composition

Baseline: v35.00 source line navigation (only promote after v35 Android test green).

Original 2022 Global event backgrounds, sprite expression frames, source speaker changes and `PARAM id=2` character X/Y metadata were previously rendered in separate panels. This version adds a **single composited mobile cutscene preview**: for supported dialogue lines, the exact recovered original PNG expression is overlaid onto its corresponding original dungeon JPG background. The speaker's source coordinate sign determines left/right placement; source X/Y are displayed with a clear warning that the original pixel transform and camera choreography are not restored.

The visual composition is strictly additive. It hides the duplicate portrait panel only while both source files and their metadata match the unlocked current original scene. Missing or unsupported frames retain the existing reader. On close, the legacy portrait panel is restored. All 20 supported scenes retain source gating. No network access, save-key or Android app identity changes. No gameplay effects, enemy data, or native animations are invented.

Chromium tests cover scene visibility, Mistral Tilith, Morgan Karl-to-Seria transition, source asset joins, and restoration on close. Packaged APK regression validates offline signer/save identity.
