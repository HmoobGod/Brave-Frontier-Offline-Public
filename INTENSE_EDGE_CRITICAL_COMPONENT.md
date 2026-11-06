# Intense Edge: critical damage component

The committed original2022 master catalog joins unit10025 (Inferno Beast Zegar)
to leader skill1313, `31@34`, `50,0,0,0,0,0@0.5`. The separately recovered Global
English name and description identify Intense Edge as a compound Spark/critical
damage effect. This patch implements only its critical component for existing
source-qualified single-hit/multi-hit normal attacks. Spark remains unimplemented;
the historical raw reader's full compound effect is not marked complete.

The catalog pins `F_LEADER_SKILL_MST_Ver749.json` SHA256
`65e591557264d656be2408e9c426ef35050b960f1736a488da8f0a55a5e845fe` and both unit
masters. This run uses committed evidence, not a newly downloaded/rehashed private
owner archive. No source tables are modified.

Independent contemporary community corroboration:

- [Global batch review, January27,2015](https://bravefrontierglobal.blogspot.com/2015/01/6-star-units-released-on-global-server.html),
  LS entry lines90–92: Zegar's leader effect has a50% critical damage bonus.
  Its separate SBB20% entry is not used for this leader component.
- [Raid squad guide](https://bravefrontierglobal.fandom.com/wiki/User_blog%3AMich%2C_Michele_%26_Kuhla/Guide%3A_Squad_building_-_Raid_Edition)
  gives worked examples adding critical bonuses to the base1.5 multiplier.
  These are community references, not recovered native engine code. Direct
  Fandom page retrieval was blocked; cached search text supplied that formula.

Accordingly, +0.5 changes an existing successful normal critical from1.5× to2×.
No critical probability, base damage formula, native rounding order, BB/SBB/UBB,
enemy criticals/resistance, friend leader, sphere, Spark, reward or save rule is
introduced. Existing per-hit flooring/KO checks and10% base chance are preserved.
The pure base-critical helper APIs remain unchanged; optional dispatch hooks
return the old result when this component is absent or ineligible.

Eligibility requires owned first squad member/effective form and the actual
battle leader to agree, exact raw master and English records, archive mode,
and a living active source-listed recipient in the current battle normal action.
Changing only a preview, mismatching the battle leader or switching to training
cannot grant the bonus. Existing leader-through-KO policy is retained. The
component does not write P, storage, stats, action targets or save schemas.

`test_bf_leader_critical_bonus.py` exercises actual queued turns for one-hit40011
and multi-hit10011 with matching/wrong leaders and critical/noncritical rolls,
exact per-hit multipliers/HP loss, disabled queued-SBB normal fallback for both
profiles, a KO/landed-crystal audit, negative eligibility controls and full
synthetic P/storage/write preservation. The merged SBB fallback wrapper loads
after the normal observers in the combined regression, matching native order. The existing v93 runtime job invokes it;
the existing v93 APK gate requires byte-exact packaging of all three modules.
No new workflow rules/triggers, signing, permissions or Gradle changes.

Fresh workflow asset preparation on the selected integration base is verified
in an isolated stage. Native Java loader compilation/packaging, fresh exact-head
Android CI and independent review must qualify the selected head/base; older
builds and reviews do not authorize later refreshes. No actual
device, real-save, native full damage or complete leader-skill parity claim.
