"""v0.49: stage source-verified 2022 Global Remains of Mirza quests.

Adds missions 60–63 and original dungeon_battle_10600.jpg. No native
encounter/drop logic is inferred, and preexisting v7 saves are untouched.
Requires v0.48 and Magutagal source preparers first.
"""
from pathlib import Path
import hashlib, json

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / 'app/src/main/assets'
m = json.loads((ROOT / 'source_data/bf_global_remains_mirza_v049.json').read_text('utf-8'))
assert m['schema'] == 'bf-global-remains-mirza-v049'
src, d, q = m['sources'], m['dungeon'], m['quests']
assert src['masterSha256'] == '69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9'
assert src['languageSha256'] == '4dccce4eeb6a89cc0cf5718badff7af95046c891882e42c05c6eaca81f9d6285'
assert src['artZipSha256'] == 'a748f675fd8271c0f41bb0b9244c83ffc5d23b4051cfd757494d16735c506644'
assert (d['id'],d['areaId'],d['landId'],d['x'],d['y'],d['requires']) == (60,100,1,425,343,53)
assert [row['missionId'] for row in q] == [60,61,62,63]
assert [(row['requires'],row['battles'],row['energy'],row['exp'],row['zel'],row['karma']) for row in q] == [
    (53,6,4,44,400,0), (60,6,4,51,450,0),
    (61,6,5,62,500,0), (62,7,7,89,600,0)]
assert all(row['dungeonId']==60 and row['background']=='dungeon_battle_10600.jpg' for row in q)
assert [row['id'] for row in m['english']] == [60,61,62,63]
assert all(row['key'] == f"MST_DUNGEONS_MISSION_{row['id']}_NAME" and
           row['descriptionKey'] == f"MST_DUNGEONS_MISSION_{row['id']}_DESCRIPTION"
           for row in m['english'])
original = ROOT / 'source_assets/bf1/dungeon/dungeon_battle_10600.jpg'
raw = original.read_bytes()
assert len(raw) == 66699 and hashlib.sha256(raw).hexdigest() == src['backgroundSha256']
assert raw[:3] == bytes((0xff,0xd8,0xff)), 'archived background is not a JPEG'
asset = ASSETS / 'content/dungeon/dungeon_battle_10600.jpg'
asset.parent.mkdir(parents=True, exist_ok=True)
if not asset.exists() or asset.read_bytes() != raw:
    asset.write_bytes(raw)
assert asset.read_bytes() == raw

html = ASSETS / 'index.html'
s = html.read_text('utf-8')
for mark in ('/* BF_MAGUTAGAL_WETLANDS_V047 */','/* BF_GLOBAL_QUEST_TEXT_DATA_V048 */'):
    assert s.count(mark) == 1, mark
assert 'bf_global_offline_demo_v7' in s
assert 'window.BF_QUEST_CATALOG.push(' in s
assert s.count('window.BF_QUEST_BACKGROUNDS=') == 1
marker = '/* BF_REMAINS_OF_MIRZA_V049 */'
quests = 'window.BF_QUEST_CATALOG.push(' + ','.join(
    json.dumps(item,ensure_ascii=True,separators=(',',':')) for item in q) + ');'
desc = {row['id']:row['description'] for row in m['english']}
text = 'window.BF_QUEST_ENGLISH_DESCRIPTIONS_V049=Object.freeze(' + json.dumps(
    desc,sort_keys=True,separators=(',',':'),ensure_ascii=True).replace('<','\\\\u003c') + ');'
oldbg = 'window.BF_QUEST_BACKGROUNDS["dungeon_battle_10500.jpg"]="content/dungeon/dungeon_battle_10500.jpg";'
newbg = 'window.BF_QUEST_BACKGROUNDS["dungeon_battle_10600.jpg"]="content/dungeon/dungeon_battle_10600.jpg";'
if s.count(marker) == 1:
    assert s.count(quests) == s.count(text) == s.count(newbg) == 1
    print('PASS v0.49 original Mirza quests already staged')
else:
    assert s.count(marker) == 0 and s.count(quests) == 0 and s.count(text) == 0
    assert s.count(oldbg) == 1 and s.count(newbg) == 0
    s = s.replace('window.BF_QUEST_BACKGROUNDS=',marker+quests+text+
                  'window.BF_QUEST_BACKGROUNDS=',1)
    s = s.replace(oldbg,oldbg+newbg,1)
    assert s.count(marker) == s.count(quests) == s.count(text) == s.count(newbg) == 1
    html.write_text(s,'utf-8')
    print('PASS v0.49 original Remains of Mirza 60–63; source JPEG; v7 save unchanged')
