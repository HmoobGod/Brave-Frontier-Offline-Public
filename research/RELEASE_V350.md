# Brave Frontier Global v3.50.0-demo — Reversible Tactical Training and Battle Presentation

Base: v3.00.0-demo, Build #167, SHA 38830d3f879cf904a6051dbb81b7a221b187cf92.

The existing optional 21-mission 2014 historical tactical practice now has:
- Undo up to 20 completed synthetic team rounds, including across wave transitions and after trial victory/defeat. Undo restores the exact cloned party/enemy HP, Burst, kits, all planned actions and log/counters before that round. Undo is exclusively in RAM; exiting resets its history.
- Bounded auto-play of up to five rounds per button click. Internal method permits at most fifteen per call; no uncontrolled timer or background execution. It uses existing deterministic Auto Plan and full round resolution.
- Tactical party and foe cards with HP bars. Owned units use the actual equipped 2022 source identity/portrait. Historical enemies display a 2022 encyclopedia unit thumbnail **only when available**, clearly labeled as **not an authenticated 2014 battle sprite**.
- Improved accessible HP progress and separate history/undo controls, while retaining the older v3.00 manual-action options, six-unit action sequencing and enemy-wave slot targeting.

**No authentic combat restoration claim.** This is a separate synthetic practice engine; true Global late-game quests, 2022 encounter formations, native damage/AI, rewards, summon economy and complete playable encyclopedia are not yet restored. 2014 source records are provenance-tagged historical approximations only.

Preserved Android package identity, existing signing key, v7 save and all 106 curated original Global quest texts, three regions and 23 dungeons. All optional practice modes remain isolated from the original player and real battle state; nothing calls saveProgress or localStorage. CI must validate full previous regressions, undo exact restoration, Android build and original package/signing.
