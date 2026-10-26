# Brave Frontier Global v2.50.0-demo — Isolated Six-Unit Squad Training

Baseline: successful v2.00 Build #161, commit ab3248767de6193ced8536c2e1743d867da010cd.

The new optional **Squad Training Lab** opens alongside v2.00's historical 2014 encounter research (21 missions, 112 waves). It clones up to six **currently owned and equipped** units from the actual v7 local squad (P.squad and P.roster), taking name, element, portrait and original 2022 Global base HP/ATK/DEF/REC from effectiveUnit(). Each practice member has separate temporary simulated HP and Burst status.

For unlocked archived missions, players can select a unit and enemy, practice Attack / Burst / Guard / Heal Kit actions, or run Auto Turn. The exercise progresses through the selected archive's recorded **2014** enemy names, recorded wave membership and enemy stats. Trial damage, defenses, healing, targeting and gauges are **synthetic and not original Brave Frontier combat**. No original SBB/BB skill effect, spawn odds, AI logic or hit-animations are claimed restored.

Practice is never saved; it contains cloned RAM-only units, does not write localStorage, alter v7 player state, summon, level, change roster or unit forms, deduct Energy, award drops or Zel/EXP/Karma, or modify original quest clears. The official 2022 original story path (106 quests, 23 dungeons, 3 maps), and all existing demo content remain unchanged.

Caveats: The historical 2014 mission-name correspondence does not confirm enemy wave arrangements used in 2022. The original 2022 encounter tables, native damage formulas, full AI, drops and later world regions remain unimplemented. v2.50 means a development milestone, not complete Brave Frontier Global restoration.

CI must pass browser save-isolation tests, UI action regression, Android APK packaging and the historical full suite. Android hardware installation/testing remains pending until the user reports it. Export your save first; install the APK over existing storage using the unchanged app ID and signing certificate.
