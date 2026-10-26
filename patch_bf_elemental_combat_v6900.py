"""Idempotent v69 source-element overlay, preserving exact prototype formula text.

Only known original base elements receive a modifier. Old browser regressions
check the original prototypeDamage expression; keep it byte-for-byte inside
a guarded, optional post-core scaling wrapper.
"""
from pathlib import Path
R=Path(__file__).resolve().parent
p=R/'app/src/main/assets/index.html'
s=p.read_text('utf8')
assert 'bf_global_offline_demo_v7' in s
assert s.count('BFGlobalBurstRecipientRecoveryV6700?.healAmount(base,ally)')==1
player='prototypeDamage(effectivePlayerAtk(p),foe.def,bbDamageMultiplier(p,burst))'
enemy='prototypeDamage(enemy.atk,target.def,target.guard ? .5 : 1)'
player_new=('((total)=>window.BFGlobalElementalCombatV6900?.scaleDamage('
    'total,UNIT_BY_ID.get(p.unitId)?.element,foe.element)??total)('+player+')')
enemy_new=('((total)=>window.BFGlobalElementalCombatV6900?.scaleDamage('
    'total,enemy.element,UNIT_BY_ID.get(target.unitId)?.element)??total)('+enemy+')')
assert s.count('function prototypeDamage(')==1
if s.count(player_new)==1 and s.count(enemy_new)==1:
    print('PASS v69 original expression retained, elemental hooks already present')
else:
    assert s.count(player)==1,('Unexpected normal/BB hit anchor',s.count(player))
    assert s.count(enemy)==1,('Unexpected enemy hit anchor',s.count(enemy))
    assert 'BFGlobalElementalCombatV6900' not in s
    out=s.replace(player,player_new,1).replace(enemy,enemy_new,1)
    assert out.count(player)==1 and out.count(enemy)==1
    assert out.count('BFGlobalElementalCombatV6900?.scaleDamage(')==2
    p.write_text(out,'utf8')
    print('PASS v69 exact original prototype formulas preserved with optional element scaling')
