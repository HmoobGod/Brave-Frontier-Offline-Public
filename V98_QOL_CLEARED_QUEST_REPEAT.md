# Brave Frontier Global Offline — v98.00 QoL Cleared-Quest Repeat

Parent: v97 local-backup feature branch (not promoted until its CI gate passes).

## Gameplay-safe workflow
- After successfully finishing a previously-cleared quest, open the QoL panel in Quest and choose **2 / 5 / 10 additional clears**.
- Uses the pre-existing v30 Replay Mission implementation and the native v7 Auto Battle control. No direct battle engine, enemy, damage, mission rewards, EXP, Zel, Karma or Energy edits.
- Every repeat requires a **new confirmed quest-clear count** before the controller permits another replay.
- Fails closed on defeat, source mission change, mode change, player disabling Auto Battle, page/background interruption, unconfirmed clear, or native replay failure.
- Does not run offline/in the background and does not persist an auto-repeat session. Auto-repeat does not claim original native Energy or drop behavior.
- Before starting, require the existing result API to report a completed, eligible victory and existing saved mission clear. Never automatically repeat an uncleared quest.

## Testing and safe promotion
- New headless Chromium state-machine tests with negative gates and bounded completion.
- New Android APK packaging/signing/save-identity test.
- Existing comprehensive original-gameplay and save regressions remain required.
- Android device testing needed before declaring in-game replay timing fully verified.

## Remaining backlog
Expanded battle speed, optional animation skip, advanced Smart Auto, saved squad presets, unit favorites/locks, evolution material tracking improvements, detailed battle HUD, and previously-read dialogue skip remain requested but unimplemented here. v97 rotating local save backups are carried forward.
