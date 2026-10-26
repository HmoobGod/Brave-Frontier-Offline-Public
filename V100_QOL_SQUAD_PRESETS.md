# Brave Frontier Global Offline — v100.00 QoL Squad Presets

Parent: isolated v99 speed feature branch. Do not promote v100 until its own CI passes, and prior v98/v99 checkpoints have successful verification.

## Functionality
- Add **five user-named squad slots** to the existing Units → Squad Setup area.
- Saving a preset only records a copy of current owned base-ID selections under a separate app-local QoL key. It does not spend items or alter the active squad.
- Applying a preset requires every chosen ID still exist in the owned roster, 1–6 unique members, and an idle battle.
- Uses the existing native saveProgress() mechanism and existing reset()/renderProgress() path. On save failure, restores P.squad to its previous in-memory value and does not reset the battle.
- Never auto-applies presets; names are sanitized and bounded, and imports or older saves cannot force invalid or unowned units into the squad.
- Local preset labels/settings are NOT part of exported v7 game-save JSON; no save migration.

## Non-goals
- Does not create new unit forms, duplicate/sell/fuse units, override original evolution, or change battle/quest rewards.
- Device test still needed for Android rendering and in-place install verification.

Next requested features: favorites/locking, material tracker improvements, advanced auto AI, detailed combat information, and skip previously viewed story dialogue.
