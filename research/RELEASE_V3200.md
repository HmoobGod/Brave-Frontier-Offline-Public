# Brave Frontier Global v32.00 — Extended Offline Combat Journal

Baseline: staged v31.00, branch feature/global-battle-focus-v3100. Promote only if its exact-source CI passes.

Captures original *demo engine log messages* from DOM MutationObserver childList records, including previously capped 9-line entries that the original `msg()` immediately trims. Records are bounded to 400 per in-memory run, labeled with observed wave/round numbers. On the existing native Restart or quest-selection reset, the previous run remains readable in the app; a new run starts. Players can select read-only report text for manual copying on Android, no download or file permissions necessary.

The journal makes no claims about recovering original 2022 damage formulas, AI, enemy identities or wave tables. No game state writes, progress modifications, network traffic, log injection or additional Android permissions. This is a **development/debugging and player-accessibility feature**, not native BF telemetry.

Required: 30+ log entries tested despite 9-line native DOM cap, reset/previous preservation, no save mutations, entire inherited regression suite and Android package test. Physical device test still pending.
