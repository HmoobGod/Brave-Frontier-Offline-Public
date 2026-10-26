# Brave Frontier Global v20.00 — Live Campaign Battle Status & Next-Mission Flow

Baseline: verified v19.00 Build #204, commit 5f615a3e503ad71079022ed5c0798ce84ced1cab.

Player-facing quest milestone: each selected original 2022 Global archived mission now has a live, read-only quest combat status pane alongside the existing playable demo battle. It shows the actual demo wave index (0-based engine state presented as 1-based), the archived mission's stage count in archive mode, live surviving squad/enemy numbers from the *existing engine*, and whether victory/defeat has occurred.

After an actual campaign victory, the NEXT control finds the next source-ordered, unlocked, uncleared archived mission, and routes through the already shipped original quest chooser (which owns reset/background/save safety), then chooses the correct region tab. Selection cannot bypass requirements, start during a busy combat turn, or run from the separate training mode. No battle automation, win simulation, or resource grant is added.

Provenance: names, dungeons and mission battle counts are sourced from the recovered 2022 Global archive; enemies, wave formations, AI, damage formulas, loot and Energy remain DEMO. This does NOT restore native original Global combat.

Implementation is additive and under Android's 64KiB per-script limit, with source HUD test and signed-APK packaged test. The v7 save key/schema, package ID, signing identity, offline permission policy, prior quests, optional A/B combat tools, and all archival data remain unchanged. Android physical device testing still required.
