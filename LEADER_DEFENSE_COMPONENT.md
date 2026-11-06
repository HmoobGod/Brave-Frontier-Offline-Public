# Ruin God's Epidemic: bounded DEF-ignore component

Original2022 unit60025 (Shadow Ronin Mifune) maps to leader1314,
`31@29`, `50,0,0,0,0,0@15` in the committed v112 master catalog. The separately
recovered Global English name/description identifies Spark plus a chance to
ignore DEF. The catalog pins `F_LEADER_SKILL_MST_Ver749.json` SHA256
`65e591557264d656be2408e9c426ef35050b960f1736a488da8f0a55a5e845fe`.
The private master archive was not newly downloaded/rehashed in this run.

The [January27,2015 Global batch review](https://bravefrontierglobal.blogspot.com/2015/01/6-star-units-released-on-global-server.html)
independently quantifies this leader's DEF-ignore chance as15% (LS section,
lines182–186). This is community corroboration, not recovered native code.

This component applies only to existing source-qualified SINGLE-HIT normal
attacks. One attempt has one potential hit, avoiding guesses about multi-hit
proc timing. A successful15% roll passes DEF0 into the existing DEMO formula;
it never changes the enemy's stored DEF. The existing critical wrapper, element
scaling, base formula and rounding remain in place. Spark, full compound-skill
coverage, multi-hit/BB/SBB/UBB DEF ignore, friend leaders, spheres, native enemy
immunity/resistance and native RNG/damage order are not implemented or claimed.

Qualification requires the owned first squad/effective form and actual battle
leader to agree, exact raw/English source records, current living active actor,
one sourced normal hit and a living resolved target. The context is limited to
that awaited action and restored in finally; enemy-phase/unrelated damage calls
cannot inherit the bypass. Existing leader-through-KO policy is preserved.
Random15% sampling uses the current DEMO Math.random model; this does not claim
to reproduce the original client's RNG stream or draw order relative to criticals.

The actual-turn regression compares a proc with a zero-DEF control, tests the
15% boundary and wrong leader, combines critical/Injury, excludes multi-hit/BB/
Guard, and runs actual default Auto against its zero-DEF control. All17 turns
preserve enemy DEF, actor base ATK, full synthetic P/storage/write counts and
leave the enemy alive. Additional source/ownership/mode/form/context and module
idempotence checks apply. No owner progress, inventory or save fields change.

The existing v166 leader runtime job invokes the new regression, and its APK
gate requires byte-exact new-module packaging and native loader order. No new
workflow rules/triggers, Gradle, signing or permissions. Selected-base prepared
core and isolated combined-module probes are recorded separately: the latter
load the Intense Edge and outer SBB modules to check wrapper coexistence, without
claiming those prospective sources are already integrated. Fresh exact-head
Android Java compilation/packaging and independent review are required before
integration; historical builds do not qualify later heads or bases.
Browser results do not establish physical-device or real-save compatibility.
