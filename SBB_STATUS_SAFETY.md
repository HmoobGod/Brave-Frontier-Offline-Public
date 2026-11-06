# Experimental SBB: existing status safety

Curse's queued-action handler previously recognized only `burst`. The optional
`sbb_demo` action could therefore bypass the lock, consume its gauge and damage
all foes while cursed. The SBB button also allowed disabled units to queue it.

The Curse handler now converts both queued BB and experimental SBB actions to
the existing normal-attack fallback. The experimental SBB queue and exported
perform function check the existing Curse and Paralysis APIs at call time.
Execution checks cover statuses inflicted after an otherwise valid queue.
Direct prototype calls also reach the existing status-aware fallback: cursed
units perform a normal attack with gauge gain blocked, paralyzed units skip.
Cure restores the existing prototype and its ordinary gauge cost.

Optional API checks preserve the legacy SBB prototype when status modules are
absent. Experimental SBB remains off by default, uses the existing DEMO 100%
gauge and prototype damage/hits, and does not reconstruct original SBB mechanics.
Source names/targets, ailment durations/cures, damage, rewards, source inventory,
save schema, Gem/Imp adjustments, signing and Android runtime code are unchanged.

The regression first reproduced the old cursed queue/direct-call failure, then
checks queue rejection, direct calls, infliction after queue, actual fallback
damage/gauge behavior, and actual all-enemy SBB after cure for both status codes.
Full synthetic player/storage/write count must remain unchanged. Existing SBB,
Curse and Paralysis regressions remain required, and packaged guards check both
status checks and the expanded queued-action handler. No owner save or installed
APK is used. Physical-device and real-save acceptance remain unverified.
