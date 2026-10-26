"""v0.51: source-verified Global Tower of Mistral, original quests 81–85.

Stages archived 2022 master metadata, English sgtext and the authentic
dungeon JPEG. Does not guess encounters, native drops or item rewards.
Does not alter saved progress (bf_global_offline_demo_v7).
"""
from pathlib import Path
import hashlib, json

ROOT=Path(__file__).resolve().parent
ASSETS=ROOT/'app/src/main/assets'
m=json.loads((ROOT/'source_data/bf_global_tower_of_mistral_v051.json').read_text('utf-8'))
assert m['schema']=='bf-global-tower-of-mistral-v051'
src,d,q=m['sources'],m['dungeon'],m['quests']
assert src['masterSha256']=='69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9'
assert src['missionSha256']=='d4e364b6c1c5a825c0153c57bdd4123cd35800c74db795d913d119b6c9a99f83'
assert src['languageSha256']=='4dccce4eeb6a89cc0cf5718badff7af95046c891882e42c05c6eaca81f9d6285'
assert src['artZipSha256']=='a748f675fd8271c0f41bb0b9244c83ffc5d23b4051cfd757494d16735c506644'
assert (d['id'],d['name'],d['areaId'],d['landId'],d['x'],d['y'],d['requires']) == (
    80,'Tower of Mistral',100,1,330,193,73)
assert [x['missionId'] for x in q]==[81,82,83,84,85]
assert [(x['requires'],x['battles'],x['energy'],x['exp'],x['zel'],x['karma']) for x in q]==[
    (73,7,5,70,500,0),(81,7,5,90,550,0),(82,7,6,110,600,0),
    (83,7,6,130,650,0),(84,8,8,180,800,0)]
assert all(x['dungeonId']==80 and x['background']=='dungeon_battle_10800.jpg' for x in q)
assert [x['id'] for x in m['english']]==[81,82,83,84,85]
assert all(x['key']==f"MST_DUNGEONS_MISSION_{x['id']}_NAME"
    and x['descriptionKey']==f"MST_DUNGEONS_MISSION_{x['id']}_DESCRIPTION"
    and x['name'] and x['description'] for x in m['english'])
source=ROOT/'source_assets/bf1/dungeon/dungeon_battle_10800.jpg'
original=source.read_bytes()
assert len(original)==46410
assert hashlib.sha256(original).hexdigest()==src['backgroundSha256']
assert original[:3]==bytes((255,216,255))
destination=ASSETS/'content/dungeon/dungeon_battle_10800.jpg'
destination.parent.mkdir(parents=True,exist_ok=True)
if not destination.is_file() or destination.read_bytes()!=original:
    destination.write_bytes(original)
assert destination.read_bytes()==original

html=ASSETS/'index.html'
s=html.read_text('utf-8')
for mark in ('/* BF_MONSTERS_NEST_V050 */',
             '/* BF_REMAINS_OF_MIRZA_V049 */',
             '/* BF_GLOBAL_QUEST_TEXT_DATA_V048 */'):
    assert s.count(mark)==1,mark
assert 'bf_global_offline_demo_v7' in s
marker='/* BF_TOWER_OF_MISTRAL_V051 */'
quests='window.BF_QUEST_CATALOG.push('+','.join(
    json.dumps(r,separators=(',',':'),ensure_ascii=True) for r in q)+');'
descriptions={r['id']:r['description'] for r in m['english']}
english='window.BF_QUEST_ENGLISH_DESCRIPTIONS_V051=Object.freeze('+json.dumps(
    descriptions,sort_keys=True,separators=(',',':'),ensure_ascii=True).replace('<',r'\\u003c')+');'
oldbg='window.BF_QUEST_BACKGROUNDS["dungeon_battle_10700.jpg"]="content/dungeon/dungeon_battle_10700.jpg";'
newbg='window.BF_QUEST_BACKGROUNDS["dungeon_battle_10800.jpg"]="content/dungeon/dungeon_battle_10800.jpg";'
if s.count(marker)==1:
    assert s.count(quests)==s.count(english)==s.count(newbg)==1
    print('PASS v0.51 Tower of Mistral already staged from archived original')
else:
    assert s.count(marker)==s.count(quests)==s.count(english)==s.count(newbg)==0
    assert s.count(oldbg)==1 and s.count('window.BF_QUEST_BACKGROUNDS=')==1
    s=s.replace('window.BF_QUEST_BACKGROUNDS=',marker+quests+english+
                'window.BF_QUEST_BACKGROUNDS=',1)
    s=s.replace(oldbg,oldbg+newbg,1)
    assert s.count(marker)==s.count(quests)==s.count(english)==s.count(newbg)==1
    html.write_text(s,'utf-8')
    print('PASS v0.51 original Tower of Mistral 81–85, original JPG, v7 untouched')
