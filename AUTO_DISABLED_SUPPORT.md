# Smart Auto: support eligibility and strength

Smart Auto previously treated a paralyzed or cursed ready ATK-buffer as a
candidate for the round's strongest support BB. When that candidate suppressed
another usable buff, the actual execution hooks skipped the paralyzed caster
or converted the cursed BB to an attack. No support buff was applied.

Coordination now excludes casters blocked by the existing Paralysis action or
Curse BB checks from its ATK-buff competition. It leaves queued actions to the
existing status handlers. A weaker caster can apply its source-backed buff;
cure or expiry immediately restores the stronger caster's eligibility. Optional
checks preserve the earlier behavior when status modules are not loaded.

This changes the optional Smart Auto support policy. Default Smart
Auto remains off; legacy Auto, manual actions, source support values, status
duration/cure behavior, damage, rewards and saved progress are unchanged. The
policy is DEMO QoL, not reconstructed native Global AI.

`test_bf_auto_disabled_support.py` reproduces the old failure using the actual
prepared game, original support identities and real ailment modules, then checks
both Paralysis and Curse through actual planned BB execution, cure and expiry.
Full synthetic player/storage/write-count state must remain unchanged. The
existing coordination and Advanced Auto regressions remain required. The APK
gate requires the new status checks in the packaged coordination code.

Smart Auto also used only level-one buff strength while combat could use the
existing verified BB-level preview. A selected Lv10 #40021 gives +40%, but Auto
previously skipped it when all allies already had +35%. Both usefulness checks
and strongest-caster coordination now use the combat module's current strength,
with original Lv1 fallback when the preview/module does not apply. Equal actual
strength retains the earlier squad slot. Source BB tables are not changed;
preview selection remains temporary and does not grant saved mastery.

The strength regression verifies an actual +35→+40 BB upgrade and an actual
Lv10 +50% tie, Lv1/absent-module fallback and Advanced Auto delegation. QoL
preference setup writes only its isolated fixture key; combat leaves the full
synthetic player/storage/write count unchanged after setup.

No owner save, APK, signing identity, Gem/Imp setting or Android runtime code is
modified. Physical-device and real-save compatibility are not established here.
