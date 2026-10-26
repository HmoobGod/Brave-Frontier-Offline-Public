"""Safely add source-referenced recipient REC to original base BB heals.

Run after original BB support and all index asset preparers. Idempotent with
strict guards. Absence of this optional JS module retains the old base heal.
"""
from pathlib import Path
R=Path(__file__).resolve().parent
f=R/'app/src/main/assets/index.html'
s=f.read_text('utf8')
assert 'bf_global_offline_demo_v7' in s
assert s.count('/* BF_GLOBAL_BB_SUPPORT_V029 */')==1
assert s.count('source Lv1 base healing range')==1
anchor='const heal=Math.max(0,Math.min(ally.maxHp-ally.hp,base));'
new='''// Source/community-verified recipient REC term. The original healer REC
    // coefficient and exact rounding are not decoded.
    const heal=Math.max(0,Math.min(ally.maxHp-ally.hp,
      window.BFGlobalBurstRecipientRecoveryV6700?.healAmount(base,ally)??base));'''
if s.count(new)==1 and anchor not in s:
    print('PASS existing v67 recipient REC hook verified; no duplicate patch.')
else:
    assert s.count(anchor)==1,('Unexpected BB healing hook',s.count(anchor))
    assert 'BFGlobalBurstRecipientRecoveryV6700' not in s
    out=s.replace(anchor,new,1)
    assert out.count('BFGlobalBurstRecipientRecoveryV6700?.healAmount(base,ally)')==1
    f.write_text(out,'utf8')
    print('PASS v67 original Lv1 BB recipient REC term hooked with fallback.')
