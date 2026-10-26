# Brave Frontier Global v68.00 — Source-Exact BB Heal Level 1–10 Preview

Base: exact green v67.00 commit `4a761e9c0dcc076580caa49a1ee802c3c4d15c77`, Build #287.

Recovered 2022 Global `F_SKILL_LEVEL_MST_1_Ver1487.json` specifies **ten skill levels** for each of four support BBs: 20041 Cure Light, 30041 Arcanadia, 40041 Cure Drill and 50041 Saint Benediction. Their common source effect code is 1500; the base HP range begins at **600–800 (Lv1)** and rises exactly **+30 minimum and +30 maximum** per level through **870–1070 (Lv10)**. The archived undecoded `50,50` parameters are retained but not interpreted. This patch crosschecks all 40 source rows in browser regression.

v68 adds optional read-only-on-save **battle-local source-level preview**. Levels 1–10 are selectable while not busy in archive battles. The original source-backed Lv1 base selected by core is adjusted by +30 × (selectedLevel−1) before v67's documented recipient REC contribution. Level defaults to **1** and resets with the battle. No BB experience/skill training is fabricated; no user progress or inventory modifications. Disabling the new module makes v67 behave unchanged. Flat DEMO healing items, enemy AI, and the original unknown healer REC coefficient are unaffected.

All 40 source levels, real BB level 10 cast, UI, disabled training mode, KO exclusions, reset, unchanged v7 progress and signed offline APK checks are CI gates. This version remains a candidate until GitHub Actions passes with APK uploaded.
