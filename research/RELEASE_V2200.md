# Brave Frontier v22.00 — Original Global Event Dialogue Reader

Verified baseline v21.00 Build #207, commit 467a9c134d2c3195edeaaf71e1174a0ebca1725b.

Restores an **interactive, read-only archive reader** containing 10 original 2022 Mistral event scripts: seven dungeon introduction scripts and three explicitly mission-clear unlock messages, containing 128 extracted dialogue frames. Extraction reference: user's immutable BF1_event_part001.zip SHA256 0d6e5882aacf458740e99cc41c31bb930a1c757672fb02e0e49306dbe9a7cb8a, confirmed against mst-decoded.zip mission cutscene fields and original dungeon background references.

The reader shows only scenes unlocked by existing archived dungeon requirements or cleared quest IDs. Preserves punctuation, line breaks and [Summoner] placeholder, uses textContent (no HTML parsing), supports dialogue paging, and does not alter the save, quest state, actual battle, rewards, or any energy.

**Important:** This is not full cutscene playback. Original scene choreography, 3D character animations, event timing, rendered speech bubbles, triggered Village systems, and non-Mistral cutscenes remain unimplemented.

Release gate: complete inherited browser regression suite, new scene-reader test, offline APK build, packaged-file test. Android physical-device QA still necessary. Preserve v7 saves and prior Android signing.
