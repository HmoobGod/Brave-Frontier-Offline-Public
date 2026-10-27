# v113 — Original Leader Bonuses Now Reach All Source-Verified Playable Recipients

## Why this is necessary
v111 restored actual original elemental ATK/HP percentages from the 2022 starter leader skills in archive DEMO battle construction. But its source-only `bonusFor()` deliberately required that **both** leader and target belonged to the 30 first-starter forms. That artificially withheld the leader effect from the **42 other currently playable forms**, even when their original elements were known.

v112 successfully joined all 72 playable forms to original 2022 F_UNIT_MST_1/2_Ver1084 and F_LEADER_SKILL_MST_Ver749 unit identities, elements and raw skill IDs.

v113 extends the **recipient side only** of source-qualified leader effects. A 2★/3★ starter leader grants +25% ATK to same-element party units regardless of their own leader skill. A 4★–6★ original starter leader grants its original +50% ATK; the relevant 6★ forms also grant +10% max HP. The six-element target membership comes strictly from v112 source, not naming or unit ID arithmetic.

## Safety boundary
- **Do not activate other leaders.** Second-starter type31 Spark, alternate type5 Elemental Mitigation, and five compound @ skills remain reference-only even when their unit is the recipient of a starter leader.
- Only newly created **archive** battle party members qualify, with strong save/roster/squad, positive integer stat, source-form and base-id checks. No double-application, no modification of training, overworld progress, summon, quest rewards or storage.
- New v113 wrapper follows v111 and never re-applies v111 bonuses to the 30 original type2 forms.
- Original source % is correct; current base-level/type stats, integer rounding and final damage formula remain DEMO. Does not claim full original leader implementation.
- The signed APK must package identical source bytes to the Android-ready CI-generated HTML and must preserve original Android applicationId, debug signing secret configuration and v7 save format.

## Proof
New v113 browser test uses CI-prepared 72-form core with Fire first-starter leader and Fire second-starter/alternate recipients, off-element controls, live 6★ HP/ATK, a different type31 leader, repeated reset idempotence, training neutrality, no local save mutation and UI injection.
