"""v70 source-exact Blessing Light #20100 base healing, no invented economy."""
from pathlib import Path
import json
R=Path(__file__).resolve().parent
d=json.loads((R/'source_data/bf_global_2022_blessing_light_v7000.json').read_text('utf8'))
assert d['provenance']['archiveSha256']=='69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9'
assert d['provenance']['sourceSha256']=='0286402bad6071687a698665e4a12cafdf7aaf9bbc6c131816cd5c2235857474'
i=d['item']
assert i=={'itemId':20100,'itemName':'祝福の光','battleEffectGroupId':520,
 'targetType':1,'itemTargetArea':2,'skillTypeId':2,'passiveSkillInfo':'500,500,0,0',
 'itemMaxStack':99,'itemMaxEquipped':3}
assert d['semantics']['sourceBaseHeal']==500
js=(R/'app/src/main/assets/bf4300_source_party_heal.js').read_text('utf8')
assert js.count('/* BF_GLOBAL_SOURCE_PARTY_HEAL_V4300 */')==1
assert "passiveSkillInfo:'500,500,0,0'" in js and 'archivedBaseHeal:500' in js
assert 'Math.min(source.archivedBaseHeal,p.maxHp-p.hp)' in js
assert 'Math.min(250,' not in js
assert all(x not in js for x in ('localStorage','saveProgress(', 'BFAndroid'))
old=(R/'test_bf_source_party_heal_v4300.py').read_text('utf8')
assert 'h0+400' in old and 'h1+500' in old and 'h0+250' not in old
print('PASS v70 original 2022 Blessing Light 500 base group heal, documented limits, legacy live browser checks retained')
