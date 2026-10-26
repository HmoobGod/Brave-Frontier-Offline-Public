# Brave Frontier Global Offline — v103.00 Battle Details QoL

Parent: v102 feature candidate, not an approved release before the complete verification gate.

- Optional collapsible live read-only panel inside the native combat screen, showing ally HP/BB/Guard, enemy HP, current wave/turn and sourced one-hit/multi-hit critical counters.
- Uses only existing S state and earlier v93/v95 sources. Never recomputes or mutates damage, targeting, buffs, round progress, saved game or rewards.
- Truncated and validated numeric display values, no new storage, no source-dependent battle calculations.
- Idle panel refresh runs only when open and app is foreground; closes timer on page unload.
- Original mechanics and Android save/signing compatibility remain primary release requirements.
