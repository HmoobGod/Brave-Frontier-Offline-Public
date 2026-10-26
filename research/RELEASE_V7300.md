# Brave Frontier Global v73.00 — Correct Original Potion Ally Targeting

Base: exact green v72.00 / GitHub Actions #296 / commit ce19da936ecc74da0690bb62170a95005c3fb42f.

The 2022 translated `F_ITEM_MST_Ver1027.json` original Potion #20000 has **one allied target**, not necessarily the acting unit. In v72 its command used the same unit as both actor and recipient. v73 provides two independent selectors for the source-backed Potion: a living, free action **actor** and a wounded, living **recipient**. The shared v45 item ledger reserves Guard **only** for the actor. The original source base healing of 100–120 remains intact, with v72's clearly described DEMO roll and one session charge. Invalid targets/KO allies cannot consume stock or turns.

The `useSourcePotion(actorId,targetId=actorId)` API retains legacy callers, while the UI chooses independent actor and target. The optional +500 DEMO Potion still heals its own actor and remains in the legacy expandable section. Cures, BBs, other items, original archives and source heal/REC progression are not changed. No saved inventory, persistence, signer, package ID, permissions, or schema changes.

Browser regression tests validate actor/target separation, full-HP actor legality, KO prevention, state restoration, command UI, and no saved progress writes. Full inherited Chromium suite and signed APK packaging run in Actions. Release remains candidate until exact-green CI and artifact.
