"""Stage verified Egor Snowfield quests 30–33 before core v7 quest bootstrap."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parent
j=json.loads((R/'source_data/bf_global_egor_snowfield_v045.json').read_text())
assert j['schema']=='bf-global-egor-snowfield-v045'
assert j['sources']['masterSha256']=='69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9'
assert [q['missionId'] for q in j['quests']]==[30,31,32,33]
assert [(q['requires'],q['battles'],q['energy'],q['exp'],q['zel']) for q in j['quests']]==[(23,5,3,35,400),(30,5,3,40,450),(31,5,4,53,500),(32,6,5,83,600)]
assert (j['dungeon']['x'],j['dungeon']['y'],j['dungeon']['requires'])==(344,656,23)
original=R/'source_assets/bf1/dungeon/dungeon_battle_10300.jpg'
raw=original.read_bytes()
assert len(raw)==27958 and hashlib.sha256(raw).hexdigest()==j['sources']['backgroundSha256']
assert raw.startswith(b'\xff\xd8\xff')
target=R/'app/src/main/assets/content/dungeon/dungeon_battle_10300.jpg'
target.parent.mkdir(parents=True,exist_ok=True)
if not target.exists() or target.read_bytes()!=raw:target.write_bytes(raw)
html=R/'app/src/main/assets/index.html'
s=html.read_text()
assert s.count('/* BF_CAVE_20_END */')==1 and s.count('/* BF_EXPERIMENTAL_SBB_V044 */')==1
assert 'bf_global_offline_demo_v7' in s
marker='/* BF_EGOR_SNOWFIELD_V045 */'
payload='window.BF_QUEST_CATALOG.push('+','.join(json.dumps(q,separators=(',',':')) for q in j['quests'])+');'
background='window.BF_QUEST_BACKGROUNDS["dungeon_battle_10300.jpg"]="content/dungeon/dungeon_battle_10300.jpg";'
old='/* BF_CAVE_20_END */window.BF_QUEST_BACKGROUNDS='
boot="};</script><script>'use strict';\n/* Stage 3: six-slot state machine."
if s.count(marker)==1:
 assert s.count(payload)==1 and s.count(background)==1
else:
 assert s.count(marker)==0 and s.count(old)==1 and s.count(boot)==1
 s=s.replace(old,'/* BF_CAVE_20_END */'+marker+payload+'window.BF_QUEST_BACKGROUNDS=',1)
 s=s.replace(boot,'};'+background+"</script><script>'use strict';\n/* Stage 3: six-slot state machine.",1)
 assert s.count(marker)==1 and s.count(background)==1
 html.write_text(s)
print('PASS v0.45 original Egor mission catalog and 2022 JPG; v7 unchanged')
