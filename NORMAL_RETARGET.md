# Normal attacks after an earlier ally defeats the queued target

The existing engine's `pickTarget` selects the requested living enemy, then
falls back to the first living enemy. The normal critical and crystal-reference
handlers instead searched only the queued slot. In an actual two-ally turn,
the first ally killed slot 0 and the second damaged slot 1, but the second
attack had neither critical processing nor a crystal-reference event.

Both single-hit and multi-hit critical handlers, and the normal crystal
observer, now use the existing engine selector. Their eligibility checks and
the executor's target choice remain unchanged. They fail closed if the
selector is unavailable. No action target, enemy state, original source data,
critical chance/multiplier, damage formula, drop rate or save field is added
or rewritten by target selection. Crystal output remains reference production,
without native collection, gauge distribution or healing.

The actual-turn regression covers source multi-hit10011 and single-hit40011:
an earlier ally KO, a previously dead queued slot, a still-living target,
a paralyzed actor, and an actual default Auto-scheduled turn. It checks the surviving enemy's exact observed HP loss,
one matching critical record, reference-event target, and full synthetic
progress/storage/write-count preservation. Paralysis must still skip damage
and events. Enemies survive and no earned reward is granted.

The original baseline isolated this fix from the then-unmerged queued-Curse
dispatch hook. Current prospective integration preserves the now-merged Curse
and SBB dispatch fixes and the queued Auto/Intense Edge candidates. An additional
actual-turn probe queues valid SBB before Curse, while an earlier ally defeats
the queued enemy. The fallback now matches a normal attack on the surviving
target: identical critical records, crystal-reference events and observed HP
loss, with unchanged gauge and synthetic progress. This is combined browser
source validation; it does not replace fresh native checks for each selected
head/base. Baseline failures and candidate results are recorded separately.
Fresh GitHub Android packaging, independent exact-head review and tested
merge-checkout identity are required before integration. Local browser results
do not establish native Global damage parity, device or real-save acceptance.
