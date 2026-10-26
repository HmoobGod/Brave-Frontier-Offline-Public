"""Strict, idempotent BF Global ATK support skill levels patch.

Run after original BB support, v67 recipient REC and v69 elemental combat
patches. No invented skill level progression, saved stats, or binary rewrites.
"""
from pathlib import Path
R=Path(__file__).resolve().parent
f=R/'app/src/main/assets/index.html'
s=f.read_text('utf8')
assert 'bf_global_offline_demo_v7' in s
assert s.count('/* BF_GLOBAL_BB_SUPPORT_V029 */')==1
assert s.count('BFGlobalBurstRecipientRecoveryV6700?.healAmount(base,ally)')==1
assert s.count('BFGlobalElementalCombatV6900?.scaleDamage(')==2
anchor="if(support?.kind==='atk_buff_all'){"
addition="const pct=window.BFGlobalOriginalAtkBBLevelsV7100?.boostFor(p.unitId)??support.pct;"
old_label='ATK BOOST BASE: +'+chr(36)+'{support.pct}%'
new_label='ATK BOOST BASE: +'+chr(36)+'{pct}%'
if addition in s:
 assert s.count(addition)==1
 assert 'support.pct>=ally.atkBuff.pct' not in s
 assert 'ally.atkBuff={pct:support.pct' not in s
 assert old_label not in s
 print('PASS v71 original ATK BB level hooks already applied')
else:
 assert s.count(anchor)==1,(anchor,s.count(anchor))
 for old in ('support.pct>=ally.atkBuff.pct','ally.atkBuff={pct:support.pct',old_label):
  assert s.count(old)==1,(old,s.count(old))
 s=s.replace(anchor,anchor+"\n   "+addition,1)
 s=s.replace('support.pct>=ally.atkBuff.pct','pct>=ally.atkBuff.pct',1)
 s=s.replace('ally.atkBuff={pct:support.pct','ally.atkBuff={pct:pct',1)
 s=s.replace(old_label,new_label,1)
 assert s.count(addition)==1
 assert s.count('BFGlobalElementalCombatV6900?.scaleDamage(')==2
 f.write_text(s,'utf8')
 print('PASS v71 source ATK skill Lv1–10 with optional Lv1 fallback')
