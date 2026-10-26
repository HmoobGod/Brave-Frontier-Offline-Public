# Brave Frontier Global v3.00.0-demo — Tactical Six-Unit Rounds

Built on v2.50 Build #166, commit 116f88189f7d7e9d70d4dc253d749c173d19789e.

## New: a second, strictly isolated tactical sandbox
* Clone up to six currently owned/equipped player units' recovered
  2022 Global names and HP/ATK/DEF/REC base stats into independent memory.
* Choose among 21 source-attributed **2014 historical** wave reference
  missions. Original 2022 Global quest unlock requirements still gate access.
* Plan one action per living squad member, independently: synthetic Attack,
  Burst, Guard and Heal with explicit unit/slot selection.
* Execute all six planned ally actions before exactly one simulated enemy
  volley per round; progress the archived historical waves independently.
* Optional deterministic Auto Plan favors low-HP% allies for healing,
  charged Bursts, guarding fragile units and lowest-HP enemies.
* Show per-round event log and total simulated damage dealt/taken, enemy
  defeats and healing. All practice statistics are transient and reset on exit.

This is experimental training, not a claim to recover the original Brave
Frontier 2022 damage formulas, battle AI, Brave Burst skill effects, drops,
enemy wave scripts, spawn odds, element system or late-game content. Historical
2014 wave data is *never* represented as proof of native 2022 formations.
The original offline demo game with its 106 source quests, three regions,
23 dungeons, encyclopedia of 2,291 2022 unit entries and previous v2.50
training mode remains unchanged.

No native battle, campaign state, unit training, roster, Energy, Zel, Karma,
EXP, drops, quest completion, summon state, Android app identity, debug
signing key or save-schema-v7 change is authorized. The trial does not
access localStorage nor call the game save functions.

Android validation: CI browser tests, full inherited regressions, packaged
APK/source/signature assertions. Device installation still requires user
testing. Export the existing in-game save before in-place APK upgrades.
