# Queued Brave Burst affected by Curse: normal-action dispatch

A manual BB can be queued before Curse is applied. The existing v59 status rule
converts it to a normal attack, but that conversion occurred inside the nested
performUnit handlers. Outer normal-critical and crystal-event observers had
already seen a burst and skipped it. On actual current prepared main, an actor
queued through the BB button then cursed dealt normal damage (enemy100000 to
99701), retained100 gauge, but produced no normal critical or crystal-reference
records even with deterministic critical rolls.

The turn executor now calls the existing optional v59 blockBurst API before the
Smart support recheck and outer performUnit chain. Its existing target/fallback
and gauge lock remain authoritative. Normal attacks produced by that fallback
are visible to the same normal-hit handlers as other normal attacks. With no
Curse API, the optional hook does nothing. No new status durations, damage,
critical rates, native crystal pickups, reward/economy, SBB/UBB rules, mastery or
save fields are invented. Normal crystal records remain uncollected reference
events, not actual original recipient distribution or BB charging.

This is separate from pending #223's Auto planning/UI action choice, and uses
current main's APIs without depending on that PR or pending SBB #221. A future
wider blockBurst implementation may benefit, but this patch does not claim
complete SBB/UBB or native combat reconstruction. Direct performUnit calls that
bypass the turn executor are outside this early dispatch path.

The committed actual-turn regression queues BB through the UI, inflicts Curse,
and exercises existing normal critical/reference-event handlers for offensive
10011 and healing20041 units, retaining gauge and full P/storage/write counts.
A cured control activates BB and spends gauge again. Only synthetic fixtures;
enemy survives so no rewards are awarded. All63 fresh preparations, new cases,
legacy Curse, Smart Auto and actual support-recheck regressions passed, plus
v41 preparation idempotence. Packaged-Curse gate now checks the compiled HTML
hook and its position ahead of the existing recheck/perform call.

No main runtime status module, original data, Java, signer, schema, Gem/Imp or
owner saves are changed. Fresh exact-head GitHub Android/source CI and
independent Codex review remain pending before any normal merge. Positive APK
packaging/device acceptance is not inferred from local browser tests.
