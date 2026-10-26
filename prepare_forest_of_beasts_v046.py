"""Restore archived Global Forest of Beasts quests 40–43 (original metadata/art).

Adds to the existing v0.45 quest catalog before original v7 bootstrap.
No new save fields; original reward code/monster encounter script unknown.
"""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parent
m=json.loads((R/'source_data/bf_global_forest_of_beasts_v046.json').read_text('utf8'))
assert m['schema']=='bf-global-forest-of-beasts-v046'
assert m['sources']['masterSha256']=='69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9'
assert m['sources']['languageSha256']=='4dccce4eeb6a89cc0cf5718badff7af95046c891882e42c05c6eaca81f9d6285'
assert m['sources']['artPackSha256']=='a748f675fd8271c0f41bb0b9244c83ffc5d23b4051cfd757494d16735c506644'
q=m['quests']; d=m['dungeon']
assert [x['missionId'] for x in q]==[40,41,42,43]
assert [(x['requires'],x['battles'],x['energy'],x['exp'],x['zel'],x['karma']) for x in q]==[
 (33,5,3,36,400,0),(40,5,3,42,450,0),(41,5,4,57,500,0),(42,6,5,84,600,0)]
assert (d['id'],d['x'],d['y'],d['requires'])==(40,64,502,33)
assert all(x['dungeonId']==40 and x['background']=='dungeon_battle_10400.jpg' for x in q)
original=R/'source_assets/bf1/dungeon/dungeon_battle_10400.jpg'
raw=original.read_bytes()
assert len(raw)==55278 and hashlib.sha256(raw).hexdigest()==m['sources']['backgroundSha256']
assert raw.startswith(b'\xff\xd8\xff')
asset=R/'app/src/main/assets/content/dungeon/dungeon_battle_10400.jpg'
asset.parent.mkdir(parents=True,exist_ok=True)
if not asset.is_file() or asset.read_bytes()!=raw:asset.write_bytes(raw)
html=R/'app/src/main/assets/index.html'
s=html.read_text('utf8')
for marker in ('/* BF_EGOR_SNOWFIELD_V045 */','/* BF_EXPERIMENTAL_SBB_V044 */'):
 assert s.count(marker)==1,marker
assert 'bf_global_offline_demo_v7' in s
marker='/* BF_FOREST_OF_BEASTS_V046 */'
payload='window.BF_QUEST_CATALOG.push('+','.join(json.dumps(x,separators=(',',':')) for x in q)+');'
oldBg='window.BF_QUEST_BACKGROUNDS["dungeon_battle_10300.jpg"]="content/dungeon/dungeon_battle_10300.jpg";'
newBg='window.BF_QUEST_BACKGROUNDS["dungeon_battle_10400.jpg"]="content/dungeon/dungeon_battle_10400.jpg";'
if s.count(marker)==1:
 assert s.count(payload)==1 and s.count(newBg)==1 and s.count(oldBg)==1
 print('PASS v0.46 Forest quests already staged')
else:
 assert s.count(marker)==0 and s.count('window.BF_QUEST_BACKGROUNDS=')==1
 assert s.count(oldBg)==1 and s.count(newBg)==0
 s=s.replace('window.BF_QUEST_BACKGROUNDS=',marker+payload+'window.BF_QUEST_BACKGROUNDS=',1)
 s=s.replace(oldBg,oldBg+newBg,1)
 assert s.count(marker)==1 and s.count(payload)==1 and s.count(newBg)==1
 html.write_text(s,'utf8')
 print('PASS added source-backed Global 40–43 and Forest of Beasts original battle background, v7 untouched')
