"""v166: source-gated type5 elemental leader mitigation in incoming damage.

Only wrap the exact v69 incoming enemy hit expression. Preserve original
prototype formula, v69 elemental matchups, guard and native-unknown effects.
"""
from pathlib import Path
R=Path(__file__).resolve().parent
p=R/'app/src/main/assets/index.html'
s=p.read_text('utf8')
assert "bf_global_offline_demo_v7" in s
prior=("((total)=>window.BFGlobalElementalCombatV6900?.scaleDamage("
       "total,enemy.element,UNIT_BY_ID.get(target.unitId)?.element)??total)"
       "(prototypeDamage(enemy.atk,target.def,target.guard ? .5 : 1))")
wrapped=("((incoming)=>window.BFGlobalOriginalElementResistV16600?."
         "scaleIncoming(incoming,enemy.element,target)??incoming)("+prior+")")
assert s.count(prior)==1,("v69 enemy damage anchor changed",s.count(prior))
assert s.count('function prototypeDamage(')==1
if s.count(wrapped)==1:
    assert s.count('BFGlobalOriginalElementResistV16600?.scaleIncoming(')==1
    print('PASS v166 type5 incoming-damage hook already installed')
else:
    assert 'BFGlobalOriginalElementResistV16600' not in s
    out=s.replace(prior,wrapped,1)
    assert out.count(prior)==1
    assert out.count('BFGlobalOriginalElementResistV16600?.scaleIncoming(')==1
    assert out.count('BFGlobalElementalCombatV6900?.scaleDamage(')==2
    p.write_text(out,'utf8')
    print('PASS v166 type5 10% known-element incoming-damage hook installed')
