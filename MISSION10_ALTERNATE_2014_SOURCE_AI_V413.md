# Mission #10 — Original 2014 Alternate Source Attack Plan (v413)

**Dependent draft on PR #411, not a change to PR #411's green head.**
This work adds three *historical 2014 only* normal-attack decisions to the
alternate (08:34) fourth wave of the existing simulated practice arena.

The independently retrieved original Global 2014 captured file
"Start of Adventure_2014-14-10-08-34.json" has exact Git blob
c6a9d86b7e72a079ebdaa48b84864d078e5568e3. Its fourth-wave
Burny 10030 (HP800/ATK320/DEF50), Glowy 50030 (850/340/60), Mossy
30030 (830/340/90) EACH has:
- AI id 1, actions per turn "1~1"
- one normal "attack" action, 100% source weight, parameter "-1"
- target condition "random", target type 2, zero conditions, zero skills

A new compact immutable source evidence record and the existing historical
practice builder require the exact original 2014 source Git blob, all three
roster tuples and attack parameters. Any mismatch fails closed.

The practice planner accepts only the 08:34 alternate, only Mission #10
wave 4, exactly matching source-proven enemy state and unmodified flags.
It chooses one "attack" per living enemy and excludes KO'd enemies.
The existing practice damage, player HP/Guard/Training Burst and random
target behaviour are still explicitly **synthetic**, never native combat.

The registered full Chromium test completes all five 2014 historical
practice waves, makes the three enemy attacks visible in its battle log,
ensures "random target NOT simulated" remains visible and compares the
exact canonical player/session/v7 save values before/after. No campaign
clears, original enemy/NPC-partner AI, items, drops or user progression
are modified.

This is NOT original 2022 Global MissionStart evidence. Authentic original
2022 enemy formations: **0/106**. Never reuse these 2014 source decisions
for native 2022 encounters.

## Stack and gates

Base branch: practice/mission10-dual-2014-capture-v411 at pinned head
6b4af43e345684e73c4b5b9e15e3d7697d27d147.

PR #411 needs independent exact-head Claude approval first. This new PR
also needs its own independent exact-head review, complete signed
Android+Chromium CI, later latest-main combination validation and
postmerge main CI before any merge. No APK release/install/owner save edit.
Android signing, app package org.bravefrontier.offline and no INTERNET
permission remain unchanged.
