# v211 — Amdahl original 2022 source-pane fail-closed diagnostics

**Runtime change: developer diagnostics only. No gameplay, saves, players,
quests, currency, battle encounters, native 2022 waves, original raw source
records, audio playback, signing or Android permissions changed.**

The optional v209 Amdahl raw reference pane previously returned silently
whenever one of its source integrity guards failed. v211 preserves the same
read-only, fail-closed behavior while providing **stable, non-sensitive**
browser console warnings identifying the category of unmet prerequisite.

- Unsupported player v7 schema or a changed 106-quest playable catalogue
- Missing v206 guide, missing v206 lookup API or wrong original master /
  canonical Amdahl provenance
- Missing v151 encounter evidence lookup or source provenance mismatch
- Any 2022 original 36-row mission tuple, group reference or source join
  mismatch (without logging actual rows or evidence)
- Missing/incorrect original Amdahl guide DOM controls

Duplicate `onPageFinished` initialization is intentionally silent and
idempotent (one v209 source pane). No private user save body, quest clears,
roster, currency, raw source record or token is included in a log message.

The existing `test_bf_amdahl_guide_real_modules_v20600.py` regression,
already in full Android CI, now runs the actual v149/v151/v206/v211
script chain in Chromium and checks each diagnostic group:
wrong player version, missing v151 lookup, tampered v206 original source
SHA, tampered v151 original encounter row, missing v206 dropdown option;
then verifies that the restored original source initializes exactly
once and that the v7 player, gameplay catalog and localStorage write
counter remain identical.

This is a browser `console.warn` diagnostic, **not** a guarantee of
Android logcat output. IOException on a missing packaged JS asset is
already logged in `MainActivity.java`, which is unchanged.

### Merge gates

Because this changes the user-visible optional WebView code, **require
independent Claude review of its exact head**, full Android CI success,
and a SHA-guarded merge. The Android device/owner-save checks are still
open. Never interpret this change as native enemy formation or AI recovery.
