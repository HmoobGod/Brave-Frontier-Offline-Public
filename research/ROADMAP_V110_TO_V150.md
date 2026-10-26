# v1.10 — Original Global Quest Journal

Based on successfully verified v1.01 Build #157. Additional optional Quest screen
supports searching the **106 archived missions**, filtering by Mistral, Morgan,
St. Lamia and progress, reading each archived description and recorded wave/
energy/EXP/Zel/Karma source fields, and switching to any **currently unlocked**
quest using the game's existing selection handler.

* Locked mission details can be previewed, but cannot be selected. On each action
  the code re-checks questUnlocked() and S.busy before invoking BFQuestAreas.choose().
* Status comes from the existing \`P.questClears\`; no new save fields or localStorage
  accesses in this module. External navigation, networking, purchases and cloud
  accounts are not introduced.
* The demo does not consume original Energy or implement recovered enemy formations,
  native enemy AI, drop probabilities, native battle damage or cutscene playback.
* \`bf110_quest_journal.js\` is separate from \`bf_home_nav.js\` (Java loader cap 64 KiB).
* Playwright regression verifies 106-source join, search, locked/available/cleared
  filters, Mistral–Morgan–St. Lamia jumps, no passive save writes and schema v7.
  APK checks verify packaging and baseline assets. Real Android testing still needed.

The separate source-audit branch \`feature/encounter-source-audit-v101\` is preserved
for research; its opaque encounter tokens are NOT treated as decoded formations.

## Roadmap toward v1.50

- **1.10:** searchable original Grand Gaia quest journal and replay navigation.
- **1.20:** verify the recovered monster master ↔ sprite archive links before
  selecting native original enemies. Keep uncertain data out of live combat.
- **1.30:** implement only source-proven monster/encounter parts, if obtainable;
  document absent mappings rather than inferring from opaque mission fields.
- **1.40:** battle-mechanics fidelity work backed by original masters and tests;
  experimental behavior explicitly opt-in where proof is incomplete.
- **1.50:** integrated regression and Android device acceptance for supported
  original content; **not** a claim of full Brave Frontier Global restoration.

Use in-place APK upgrades only; export your save first, never delete app data,
and do not change the app ID, development signing key, or v7 save schema.
