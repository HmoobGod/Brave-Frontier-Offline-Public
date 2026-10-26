# Brave Frontier Global v25.00 — Source Story Cues

Baseline v24.00 original three-region dialogue reader, be5fed3e57f9c37421691bd05a69577eb55a9e25; must pass its release gate before v25 promotion.

Adds player-facing cues inside the quest experience when an originally documented clear-event script is available after victory (missions 10, 11, 21) or when a verified original dungeon introduction is available after unlocking a dungeon. The player explicitly presses READ ORIGINAL SCENE to open the read-only archive dialogue. This avoids inventing cutscene timing or silently triggering original systems that are not restored.

Event availability, mission unlocks and victory are read from existing real demo state; cue cannot grant rewards, alter parties or saved state, or launch during combat turns/training. Dismissal is session-only and does not modify v7 save. Source identities remain 2022 Global Mistral/Morgan/St. Lamia. Cave of Malice script remains excluded pending source conflict resolution.
