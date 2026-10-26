"""v0.50: source-backed original Monster's Nest missions 70-73, save v7 intact.

This stages exactly the archived quest metadata and battle art, without
inventing the original enemy waves, item drops, or native combat formulas.
"""
from pathlib import Path
import json, hashlib

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / 'app/src/main/assets'
m = json.loads((ROOT/'source_data/bf_global_monsters_nest_v050.json').read_text('utf-8'))
assert m['schema'] == 'bf-global-monsters-nest-v050'
src, d, q = m['sources'], m['dungeon'], m['quests']
assert src['masterSha256'] == '69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9'
assert src['languageSha256'] == '4dccce4eeb6a89cc0cf5718badff7af95046c891882e42c05c6eaca81f9d6285'
assert src['artZipSha256'] == 'a748f675fd8271c0f41bb0b9244c83ffc5d23b4051cfd757494d16735c506644'
assert (d['id'],d['areaId'],d['landId'],d['x'],d['y'],d['requires']) == (70,100,1,49,264,63)
assert [row['missionId'] for row in q] == [70,71,72,73]
assert [(row['requires'],row['battles'],row['energy'],row['exp'],row['zel'],row['karma']) for row in q] == [
    (63,6,4,46,400,0), (70,6,4,53,450,0),
    (71,6,5,65,500,0), (72,7,7,91,600,0)]
assert all(row['dungeonId']==70 and row['background']=='dungeon_battle_10700.jpg' for row in q)
assert [row['id'] for row in m['english']] == [70,71,72,73]
assert all(row['key'] == f"MST_DUNGEONS_MISSION_{row['id']}_NAME" and
           row['descriptionKey'] == f"MST_DUNGEONS_MISSION_{row['id']}_DESCRIPTION"
           for row in m['english'])

original = ROOT/'source_assets/bf1/dungeon/dungeon_battle_10700.jpg'
raw = original.read_bytes()
assert len(raw) == 32032 and hashlib.sha256(raw).hexdigest() == src['backgroundSha256']
assert raw[:3] == bytes((255,216,255)), 'original artwork not a JPEG'
asset = ASSETS/'content/dungeon/dungeon_battle_10700.jpg'
asset.parent.mkdir(parents=True,exist_ok=True)
if not asset.exists() or asset.read_bytes() != raw:
    asset.write_bytes(raw)
assert asset.read_bytes() == raw

html = ASSETS/'index.html'
s = html.read_text('utf-8')
for prior in ('/* BF_REMAINS_OF_MIRZA_V049 */',
              '/* BF_GLOBAL_QUEST_TEXT_DATA_V048 */',
              '/* BF_MAGUTAGAL_WETLANDS_V047 */'):
    assert s.count(prior) == 1, prior
assert 'bf_global_offline_demo_v7' in s
assert s.count('window.BF_QUEST_BACKGROUNDS=') == 1
marker = '/* BF_MONSTERS_NEST_V050 */'
quests = 'window.BF_QUEST_CATALOG.push(' + ','.join(
    json.dumps(item,separators=(',',':'),ensure_ascii=True) for item in q) + ');'
english = {row['id']: row['description'] for row in m['english']}
desc = 'window.BF_QUEST_ENGLISH_DESCRIPTIONS_V050=Object.freeze(' + json.dumps(
    english,sort_keys=True,separators=(',',':'),ensure_ascii=True).replace('<','\\u003c') + ');'
old_bg = 'window.BF_QUEST_BACKGROUNDS["dungeon_battle_10600.jpg"]="content/dungeon/dungeon_battle_10600.jpg";'
new_bg = 'window.BF_QUEST_BACKGROUNDS["dungeon_battle_10700.jpg"]="content/dungeon/dungeon_battle_10700.jpg";'
if s.count(marker) == 1:
    assert s.count(quests) == s.count(desc) == s.count(new_bg) == 1
    print('PASS v0.50 idempotent Monster\'s Nest source staging')
else:
    assert s.count(marker) == s.count(quests) == s.count(desc) == s.count(new_bg) == 0
    assert s.count(old_bg) == 1
    s = s.replace('window.BF_QUEST_BACKGROUNDS=',
                  marker+quests+desc+'window.BF_QUEST_BACKGROUNDS=',1)
    s = s.replace(old_bg,old_bg+new_bg,1)
    assert s.count(marker) == s.count(quests) == s.count(desc) == s.count(new_bg) == 1
    html.write_text(s,'utf-8')
    print('PASS v0.50 original Monster\'s Nest missions 70-73, authentic JPEG and v7')
