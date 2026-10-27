# v110 — Original 2022 Starter Leader Skill Source

Source recovered from the user's original \`mst-decoded.zip\` (SHA256 \`69c3d919903039d8e8bdfb3327909b7172d6dc77286fcfb18def2d9849d84\`).
**Note:** the exact file hash above is not a valid master provenance; see the \`source_data/bf_global_2022_starter_leader_skill_audit_v110.json\` real SHA256 \`69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9\`.

- 2022 \`F_UNIT_MST_1/2_Ver1084.json\` joins to \`F_LEADER_SKILL_MST_Ver749.json\` on \`lsId\`.
- **30 source-verified starter unit forms**: 6 elements × 5 original unit IDs each, 18 original leader skill IDs.
- 2★/3★ leader: +25% ATK of matching element.
- 4★/5★ leader: +50% ATK of matching element.
- 6★ leader: +50% ATK and +10% max HP of matching element.
- Original \`skillTypeId=2\` and exact per-leader \`passiveSkillInfo\` preserved.
- Normalized source JSON retains original unit IDs, element/leader mapping, stat percentages and file-hash provenance. A new read-only Squad Setup panel inspects the leader in squad slot 1 and eligible matching-element forms.

**Critical boundary:** source data is real, but **no battle stat bonuses are applied** until the game's party creation, type/level scaling, guest/leader rules, buff stacking and reset hooks are independently verified. The source API fails closed for any unit outside the 30 recovered starter forms.

No saved-progress field, damage, loot, summon, energy, Android package or signing identity is modified. Playwright tests cover exact source mapping and live squad lookup; signed APK tests verify source and identity. On-device verification is still outstanding.

Next: audit native party stat setup and safely implement original passive leader stat effects without double-applying attack, HP or other buffs.
