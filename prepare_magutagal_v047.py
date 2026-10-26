"""v0.47: stage verified 2022 Magutagal Wetlands quest records + original art.

Missions 50–53 added before original v7 quest engine initialization.
Enemy waves/drop/event scripts remain DEMO; old saves and combat unaffected.
"""
from pathlib import Path
import hashlib,json

ROOT=Path(__file__).resolve().parent
m=json.loads((ROOT/'source_data/bf_global_magutagal_v047.json').read_text('utf-8'))
assert m['schema']=='bf-global-magutagal-v047'
source=m['sources']
assert source['masterSha256']=='69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9'
assert source['languageSha256']=='4dccce4eeb6a89cc0cf5718badff7af95046c891882e42c05c6eaca81f9d6285'
assert source['artZipSha256']=='a748f675fd8271c0f41bb0b9244c83ffc5d23b4051cfd757494d16735c506644'
q=m['quests']; d=m['dungeon']
assert [r['missionId'] for r in q]==[50,51,52,53]
assert [(r['requires'],r['battles'],r['energy'],r['exp'],r['zel'],r['karma']) for r in q]==[
    (43,5,3,41,400,0),(50,5,3,47,450,0),
    (51,5,4,59,500,0),(52,6,5,87,600,0)]
assert (d['id'],d['areaId'],d['landId'],d['x'],d['y'],d['requires'])==(50,100,1,252,420,43)
assert all(r['dungeonId']==50 and r['background']=='dungeon_battle_10500.jpg' for r in q)
raw=(ROOT/'source_assets/bf1/dungeon/dungeon_battle_10500.jpg').read_bytes()
assert len(raw)==43940 and hashlib.sha256(raw).hexdigest()==source['backgroundSha256']
assert raw.startswith(b'\xff\xd8\xff')
asset=ROOT/'app/src/main/assets/content/dungeon/dungeon_battle_10500.jpg'
asset.parent.mkdir(parents=True,exist_ok=True)
if not asset.exists() or asset.read_bytes()!=raw:asset.write_bytes(raw)
assert asset.read_bytes()==raw

html=ROOT/'app/src/main/assets/index.html'
s=html.read_text('utf-8')
for prior in ('/* BF_EGOR_SNOWFIELD_V045 */','/* BF_FOREST_OF_BEASTS_V046 */'):
    assert s.count(prior)==1,prior
assert 'bf_global_offline_demo_v7' in s
marker='/* BF_MAGUTAGAL_WETLANDS_V047 */'
payload='window.BF_QUEST_CATALOG.push('+','.join(json.dumps(x,separators=(',',':'),ensure_ascii=True) for x in q)+');'
oldbg='window.BF_QUEST_BACKGROUNDS["dungeon_battle_10400.jpg"]="content/dungeon/dungeon_battle_10400.jpg";'
newbg='window.BF_QUEST_BACKGROUNDS["dungeon_battle_10500.jpg"]="content/dungeon/dungeon_battle_10500.jpg";'
if s.count(marker)==1:
    assert s.count(payload)==1 and s.count(oldbg)==1 and s.count(newbg)==1
    print('PASS v0.47 idempotent Magutagal quest patch')
else:
    assert s.count(marker)==0 and s.count(oldbg)==1 and s.count(newbg)==0
    assert s.count('window.BF_QUEST_BACKGROUNDS=')==1
    s=s.replace('window.BF_QUEST_BACKGROUNDS=',marker+payload+'window.BF_QUEST_BACKGROUNDS=',1)
    s=s.replace(oldbg,oldbg+newbg,1)
    assert s.count(marker)==1 and s.count(payload)==1 and s.count(newbg)==1
    html.write_text(s,'utf-8')
    print('PASS v0.47 original Magutagal missions 50–53 and archived wetland JPEG, v7 saved progress unchanged')
