# Brave Frontier Global v69.00 — Elemental Advantage in Original-Element Encounters

Parent: original healing-level v68.00 branch; preserved alongside v69 elemental combat. Require v68 verified parent before promotion.

Brave Frontier Global's original element relationships are Fire→Earth→Thunder→Water→Fire and mutually advantageous Light↔Dark. Independent contemporary/comprehensive community references identify original **150% damage when advantageous** and **50% damage when resisted**:
- https://bravefrontierglobal.fandom.com/wiki/Damage
- https://bravefrontiereurope.fandom.com/wiki/Gameplay:Elements

This release adds an optional original-element matchup calculator and two strict wrappers around the unchanged *existing DEMO* combat expressions: normal or BB player attacks use the original playable unit's sourced `UNIT_BY_ID.element` against the target's documented `enemy.element`; enemy normal attacks use its documented element against the ally's original unit element. Both element identities must exist and match the six source spellings. **Synthetic encounter monsters lack source-established elements and stay neutral**. Known original-source boss variants that already expose `element` can receive the corresponding real elemental advantage. Unknown, mixed, temporary-added and multi-element cases use the old prototype rather than fake provenance.

The original 150%/50% *relationship* is preserved; existing DEMO ATK–DEF formula, hit distributions, enemy AI, fractional rounding and animations are not claimed native. The guarded `?.scaleDamage(...)??total` wrappers preserve original prototypeDamage call text and old damage when this optional module is absent. v67 REC contribution remains unchanged. The build-time patch checks exact anchors, is idempotent and runs after v67’s healing patch; no huge index rewrite committed, no original source tables touched.

Save `P.version=7`, localStorage, APK package ID, Android development signer, source art, quest clears and offline manifest remain unchanged. Functional/browser test covers all 6 advantageous relationships, 4 resisted cases, neutral/unknown/training paths, actual normal attack HP impact, module-absent fallback and no save writes; packaged test confirms both hooks and v67 continuity. Promote only after exact successful GitHub Actions APK upload.
