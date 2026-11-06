# Experimental SBB fallback: one normal action dispatch

Turning off the optional SBB prototype after queueing, losing its required
gauge, or losing its supported source profile already falls back to a normal
attack. That conversion happened inside the base performer, which recursively
called the complete global performer again. Status modifiers such as Injury
therefore ran twice, even though the original ATK value was restored afterward.

An actual main-b712 turn with Injury and baseATK1000 dealt293 damage when queued
as a normal attack, but137 through the disabled-SBB fallback. Both restored ATK
and left synthetic progress untouched. This baseline included the actual v62
Injury wrapper; an earlier identity-only harness without v62 could not test it.

An optional outer dispatch wrapper now applies exactly the existing invalid-SBB
fallback before entering status/normal-hit handlers. It loads after all current
performUnit wrappers. Same normal target/default, gauge rule and valid SBB
behavior; no new damage formula, rate, native SBB cost/effects or save behavior.
This avoids recursive status application and lets normal critical/crystal
observers see the fallback at entry. It is idempotent and does not touch P or
storage. Invalid/foreign actors and training mode retain their original path.

The actual-turn regression compares fallback damage with a normal reference for
Injury on/off and positive ATK buffs, while checking restored base ATK, unchanged
existing DEMO gauge behavior, exactly one normal critical/reference-event record,
and whole synthetic P/storage/write-count preservation. A valid enabled SBB
control must still spend its existing prototype gauge, damage the enemy and
produce no normal-attack records. Enemies survive so no rewards are granted.

The existing v44 runtime job invokes this test; its APK gate checks the packaged
module byte-for-byte. No new workflow rules/triggers, signing, permission or
Gradle changes. Native Java compilation/packaging, exact-head GitHub CI and
independent review remain necessary; no owner-save/device acceptance claimed.

Separate pending #221 status guards and #231 early Curse dispatch are preserved.
This does not implement their Curse/Paralysis or Auto planning changes. Review
the combined normal pipeline when integrating those branches; do not infer full
SBB or native gameplay completion from this prototype fallback correction.
