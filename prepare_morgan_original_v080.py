"""v0.80 source-exact original Global Morgan map & 36 offline demo missions.

Sources: 2022 F_DUNGEON_MST, F_MISSION_MST and English sgtext.
Adds only original source names, descriptions, backgrounds, wave counts,
energy requirements (metadata), progression and EXP/Zel/Karma rewards.
No inferred enemy waves, AI, drop tables, guest units, native attack formulas.
Preserves player save bf_global_offline_demo_v7.
"""
from pathlib import Path
from zipfile import ZipFile
import hashlib,json

ROOT=Path(__file__).resolve().parent
ASSETS=ROOT/'app/src/main/assets'
data=json.loads((ROOT/'source_data/bf_global_morgan_original_v080.json').read_text('utf-8'))
assert data['schema']=='bf-global-morgan-2022-original-quests-v080'
p=data['provenance']
assert p['mastersZipSha256']=='69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9'
assert p['missionMasterSha256']=='d4e364b6c1c5a825c0153c57bdd4123cd35800c74db795d913d119b6c9a99f83'
assert p['dungeonMasterSha256']=='16f090514d65846f6bd4a9998b50d6c810bc806a79858c0ff766cdb1a22536fc'
assert p['localizationZipSha256']=='4dccce4eeb6a89cc0cf5718badff7af95046c891882e42c05c6eaca81f9d6285'
assert p['artZipSha256']=='a748f675fd8271c0f41bb0b9244c83ffc5d23b4051cfd757494d16735c506644'
assert len(data['dungeons'])==7 and len(data['quests'])==36
assert [d['id'] for d in data['dungeons']]==[200,210,220,230,240,250,260]
ids=[*range(200,205),*range(210,215),*range(220,225),*range(230,235),*range(240,245),*range(250,255),*range(260,266)]
assert [q['missionId'] for q in data['quests']]==ids
assert all(q['requires']==(ids[i-1] if i else 85) for i,q in enumerate(data['quests']))
assert all(q['dungeonId']==(200+(q['missionId']-200)//10*10) for q in data['quests'])
assert all(q['missionNameKey']==f"MST_DUNGEONS_MISSION_{q['missionId']}_NAME" and
           q['descriptionKey']==f"MST_DUNGEONS_MISSION_{q['missionId']}_DESCRIPTION" and
           q['name'] and q['description'] for q in data['quests'])
assert all(d['areaId']==200 and d['landId']==1 and d['nameKey']==f"MST_DUNGEONS_DUNGEON_{d['id']}_NAME"
           for d in data['dungeons'])
source=ROOT/'source_assets/bf1/morgan/BF1_Morgan_Original_Battle_2022_v080.zip'
original=source.read_bytes()
assert hashlib.sha256(original).hexdigest()==p['artBundleSha256']
expected=set()
with ZipFile(source) as assets:
    for dungeon in data['dungeons']:
        member='content/dungeon/'+dungeon['background']
        expected.add(member)
        raw=assets.read(member)
        assert len(raw)==dungeon['imageBytes']
        assert hashlib.sha256(raw).hexdigest()==dungeon['imageSha256']
        assert raw[:3]==bytes((255,216,255))
        destination=ASSETS/member;destination.parent.mkdir(parents=True,exist_ok=True)
        if not destination.is_file() or destination.read_bytes()!=raw:destination.write_bytes(raw)
    assert set(assets.namelist())==expected

world=ROOT/'source_assets/bf1/morgan/BF1_Morgan_Original_World_Map_2022_v080.zip'
map_hashes={'content/area/area_0002.jpg':'e4390a48e56cb1f071f299d22a89e9bbb5c90610e47b8ff4cd3ddf0a888ac0fc',
            'content/area/area_plate_0002.png':'a437f389f77e203a6d51539481d6e153e57963afb67c7e045054a212706395fd'}
with ZipFile(world) as assets:
    assert set(assets.namelist())==set(map_hashes)
    for member,sha in map_hashes.items():
        raw=assets.read(member)
        assert hashlib.sha256(raw).hexdigest()==sha
        destination=ASSETS/member;destination.parent.mkdir(parents=True,exist_ok=True)
        if not destination.is_file() or destination.read_bytes()!=raw: destination.write_bytes(raw)

html=ASSETS/'index.html'
s=html.read_text('utf-8')
assert 'bf_global_offline_demo_v7' in s
assert '/* BF_TOWER_OF_MISTRAL_V051 */' in s
assert s.count('window.BF_QUEST_BACKGROUNDS=')==1
catalog=data['quests']
appends=[{k:r[k] for k in ('missionId','label','missionNameKey','dungeonId','requires','battles','energy','exp','zel','karma')}
        for r in catalog]
for q,row in zip(appends,catalog):
    q['dungeonNameKey']=next(x['nameKey'] for x in data['dungeons'] if x['id']==row['dungeonId'])
    q['background']=next(x['background'] for x in data['dungeons'] if x['id']==row['dungeonId'])
    assert q['energy']==row['energy'] and q['background']==next(x['background'] for x in data['dungeons'] if x['id']==q['dungeonId'])
payload={'schema':data['schema'],'dungeons':data['dungeons'],
    'quests':[{k:q[k] for k in ('missionId','name','description','missionNameKey','descriptionKey','dungeonId')} for q in catalog]}
encoded=json.dumps(payload,separators=(',',':'),ensure_ascii=True).replace('<',r'\u003c')
push='window.BF_QUEST_CATALOG.push('+','.join(json.dumps(q,separators=(',',':'),ensure_ascii=True) for q in appends)+');'
reference='window.BF_MORGAN_QUESTS_V080=Object.freeze('+encoded+');'
backgrounds=''.join('window.BF_QUEST_BACKGROUNDS['+json.dumps(d['background'])+']='+json.dumps('content/dungeon/'+d['background'])+';' for d in data['dungeons'])
marker='/* BF_MORGAN_ORIGINAL_QUESTS_V080 */'
bgmarker='/* BF_MORGAN_ORIGINAL_BACKGROUNDS_V080 */'
if marker in s:
    assert s.count(marker)==s.count(bgmarker)==1
    assert s.count(reference)==s.count(push)==s.count(backgrounds)==1
    print('PASS v0.80 original Morgan quest and world art already staged')
else:
    assert s.count(marker)==s.count(bgmarker)==s.count(reference)==s.count(push)==0
    s=s.replace('window.BF_QUEST_BACKGROUNDS=',marker+reference+push+'window.BF_QUEST_BACKGROUNDS=',1)
    oldbg='window.BF_QUEST_BACKGROUNDS["dungeon_battle_10800.jpg"]="content/dungeon/dungeon_battle_10800.jpg";'
    assert s.count(oldbg)==1
    s=s.replace(oldbg,oldbg+bgmarker+backgrounds,1)
    assert s.count(marker)==s.count(bgmarker)==1
    html.write_text(s,'utf-8')
    print('PASS v0.80 Morgan 36 quests, 7 original battle JPGs and world map, save v7 intact')
