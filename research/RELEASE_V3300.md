# v33.00 — Optional Original Dialogue Auto-play

Baseline: staged v32.00 source-linked in-memory combat journal, SHA 48f504358f66826395aa67538a2a57455ae5a711. Promotion depends on v32 passing.

Opt-in original 2022 script dialogue playback: the user may use Play/Pause, adjust page delays (1.5, 2.5 or 4 seconds per page), or jump to the final page of an unlocked official text scene. The code presses the same pre-existing v22 original scene Next control, retaining source-correct original portraits/expressions (v29) and dungeon backgrounds (v27). Auto-play stops at the end or when the reader closes, app becomes hidden, scene selection changes, or user manually navigates dialogue. It never awards, fights or saves anything.

**Clarification:** The timers are new OPTIONAL QoL, not recovered official 2022 event timing. The original cutscene camera, character movement, scene choreography and sound triggers are still absent. The source dialogue itself is unchanged; user starts auto-play explicitly.

Regression covers no auto-start, exact scene, timed advance, pause, source-last-page behavior, save v7 and Android offline package.
