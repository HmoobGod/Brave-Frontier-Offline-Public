# Brave Frontier Global v11.00 — Temporary Squad Formation Control

Based on verified v10.00 Build #178, SHA 36cabbd8b88297a1071dc4798594ea5dd324f873.

The Archive Draft Lab now supports **reordering up to six selected 2022 recovered unit forms** before a synthetic tactical encounter. Each selected entry shows its slot and keyboard/accessible Up and Down movement controls. Source search, add/remove, archive evolution navigation and start flow remain unchanged. The final draft array retains that explicit order into the existing tactical round engine, which resolves allied actions in draft order. Slot ordering is a training-simulator convenience and is not a claim about authentic original Global combat formation or AI.

The feature does not modify the user's actually equipped squad, summon any archive-only units, change campaign progress, write v7 saves, or touch the debug signing identity. Archive draft is still opt-in, fully temporary and outside real gameplay; 2014 historical encounter sets remain distinct from 2022 source unit forms.

CI: exercise multi-form reorder, boundary/invalid cases, UI clicks, draft battle action order, undo integrity, actual squad and save isolation, and Android packaged assets plus previous regressions.
