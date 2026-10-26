# Brave Frontier Global v42.00 — Optional Demo Battle Potion

Baseline: verified v41.00 Build #248 (commit 0143243fbaa576d068601e2ce445bde3b3363454).

New opt-in battle item command in the existing live story-mode DEMO battle. When the squad is not executing a turn, use one of three temporary DEMO potions on an active, injured, unqueued squad member. Each restores up to 500 current HP and queues Guard as that unit's action for the turn. The Guard action is reasserted immediately before Execute to prevent queuing Attack afterward and receiving a free heal. Potions cannot be used on KO or full-HP units, while busy/finished/auto, or in training mode. Per-battle stock is reset by the existing battle reset/mission-change flow; turn usage cannot be repeated for the same unit in one round.

This is a prototype of the missing BF battle-item interaction, *not* a claim about original 2022 Potion effects, native inventory economy, recovered item animations or item use limits. The three temporary potions never enter the saved materials/inventory and cannot change P, progress, quest rewards, drops, package identity, Android permissions, or v7 saved schema. The default game battle engine and damage math remain DEMO. No physical Android testing claimed.

Release gates: headless Chromium attack-requeue, injured/KO/full HP restrictions, three-item cap, training isolation, battle reset, byte-for-byte P/save/clears equality; inherited browser regressions; signed packaged-APK script and offline identity tests.