# v111 — Source-backed 2022 Starter Leader Effects in Archive Battles

Parent: v110 recovered 30 starter forms, six elements and 18 leader skills. Provenance: 2022 F_UNIT_MST_1/2_Ver1084.json joined to F_LEADER_SKILL_MST_Ver749.json, original zip SHA256 69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9.

## Scope of live mechanics
- Only newly created archive-mode DEMO squads receive eligible recovered original leader percentages; training is unchanged.
- **Verified build-stage form injection:** checked-in index.html starts with 2★ and 3★ forms, but existing v35–v37 original-data preparation scripts add the 4★–6★ forms to the **generated APK's** playable UNIT_BY_ID using source_assets/bf1 archived packs. The signed-APK browser regression must confirm 10015 is playable and 50% ATK / 10% HP affects the newly constructed 6★ party. Never infer completeness from the pre-preparation HTML snapshot.
- First squad position is the leader. Unknown leader forms or recipient forms outside the 30 source-verified starters fail closed; matching-element units receive their own source-qualified bonus.
- Original effects: 2-star/3-star +25% ATK; 4-star/5-star +50% ATK; 6-star +50% ATK and +10% max HP.
- Hook wraps the vetted existing playerUnit(i) builder invoked in reset(), not the battle event loop. It applies once per new party unit, never repeatedly multiplies an existing ally, and never grants mid-battle HP.
- Integer floor is used in the existing DEMO stat framework for reproducibility. This numerical ordering is a DEMO integration decision: full native stat scaling, buff stacking, damage formulas and rounding have not been recovered.
- Existing P progress, v7 save schema, localStorage, quests, training battle rules, enemy combat, stamina and rewards are unchanged.

## Tests and safety
Browser tests pin the exact audited playerUnit/reset constructor signatures. The original checked-in 4.47 MB core index.html SHA256 is 82e81c853362342a753714b2569faa48e1d1fec7ac4c4676fdb419acd077a0f0, but GitHub's existing Prepare bundled HTML assets step changes the file bytes; packaged test instead byte-matches the resulting prepared HTML to the APK and check **live** 2★/3★ +25% ATK and generated 6★ +50% ATK / +10% HP from the v37 prepared playable catalog, leader rotations, no double application, repeated resets, training-mode neutrality and v7 save integrity. APK tests byte-verify packaged JS, load order, signed identity and no internet permission. Device testing remains outstanding.

## Remaining source gaps
All other leader skills, friend leader stacking, 2022 battle stat type/level rounding, sphere/passive composition, native enemies, encounter groups, loot and true native combat AI are not yet recovered. Do not infer those effects from this narrow source-backed subset.
