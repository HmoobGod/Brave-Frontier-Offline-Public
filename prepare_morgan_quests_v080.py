"""v0.80: source-authenticated Morgan offline quest expansion (36 quests).

Restores archived mission names, descriptions, map, JPEG backgrounds, requirements,
wave COUNTS and EXP/Zel/Karma, not enemy composition, loot, original damage, or AI.
Never modifies the existing Android save key or old mission catalog records.
"""
from pathlib import Path
import json,hashlib,zipfile

ROOT=Path(__file__).resolve().parent
ASSETS=ROOT/'app/src/main/assets'
DATA=ROOT/'source_data/bf_global_morgan_original_v080.json'
BATTLE=ROOT/'source_assets/bf1/morgan/BF1_Morgan_Original_Battle_2022_v080.zip'
MAP=ROOT/'source_assets/bf1/morgan/BF1_Morgan_Original_World_Map_2022_v080.zip'
m=json.loads(DATA.read_text('utf-8'))
p=m['provenance']
assert m['schema']=='bf-global-morgan-2022-original-quests-v080'
sha=lambda b:hashlib.sha256(b).hexdigest()
assert sha(BATTLE.read_bytes())==p['artBundleSha256']=='f56868eda4ec440038655086a61719bf500bd665f6795856d44f21271738f0ff'
assert sha(MAP.read_bytes())=='dfad7f363c28137176beb8fc83abe8f3ba3815c872f0e81bf60b7363356958a3'
assert p['mastersZipSha256']=='69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9'
assert p['missionMasterSha256']=='d4e364b6c1c5a825c0153c57bdd4123cd35800c74db795d913d119b6c9a99f83'
assert p['dungeonMasterSha256']=='16f090514d65846f6bd4a9998b50d6c810bc806a79858c0ff766cdb1a22536fc'
assert p['localizationZipSha256']=='4dccce4eeb6a89cc0cf5718badff7af95046c891882e42c05c6eaca81f9d6285'
assert p['artZipSha256']=='a748f675fd8271c0f41bb0b9244c83ffc5d23b4051cfd757494d16735c506644'
dungeons=m['dungeons'];quests=m['quests']
dids=[200,210,220,230,240,250,260]
qids=[*range(200,205),*range(210,215),*range(220,225),*range(230,235),
      *range(240,245),*range(250,255),*range(260,266)]
assert [d['id'] for d in dungeons]==dids
assert [q['missionId'] for q in quests]==qids and len(quests)==36
assert quests[0]['requires']==85
assert all(q['requires']==(qids[i-1] if i else 85) for i,q in enumerate(quests))
for i,d in enumerate(dungeons):
    assert d['areaId']==200 and d['landId']==1 and 0<=d['x']<=640 and 0<=d['y']<=960
    assert d['nameKey']==f"MST_DUNGEONS_DUNGEON_{d['id']}_NAME"
    assert d['background']==f"dungeon_battle_{20100+100*i}.jpg"
for q in quests:
    d=next(d for d in dungeons if d['id']==q['dungeonId'])
    assert q['missionNameKey']==f"MST_DUNGEONS_MISSION_{q['missionId']}_NAME"
    assert q['descriptionKey']==f"MST_DUNGEONS_MISSION_{q['missionId']}_DESCRIPTION"
    assert q['background']==d['background'] if 'background' in q else True
    assert q['name'] and q['description'] and q['battles']>0
    assert q['exp']>=0 and q['zel']>=0 and q['karma']>=0
with zipfile.ZipFile(BATTLE) as z:
    assert set(z.namelist())=={f"content/dungeon/{d['background']}" for d in dungeons}
    for d in dungeons:
        key=f"content/dungeon/{d['background']}"
        raw=z.read(key)
        assert len(raw)==d['imageBytes'] and sha(raw)==d['imageSha256'] and raw[:3]==bytes((255,216,255))
        dest=ASSETS/key
        dest.parent.mkdir(parents=True,exist_ok=True)
        if not dest.exists() or dest.read_bytes()!=raw:dest.write_bytes(raw)
with zipfile.ZipFile(MAP) as z:
    expected={'content/area/area_0002.jpg':('e4390a48e56cb1f071f299d22a89e9bbb5c90610e47b8ff4cd3ddf0a888ac0fc',169225),
              'content/area/area_plate_0002.png':('a437f389f77e203a6d51539481d6e153e57963afb67c7e045054a212706395fd',17075)}
    assert set(z.namelist())==set(expected)
    for key,(digest,length) in expected.items():
        raw=z.read(key)
        assert len(raw)==length and sha(raw)==digest
        dest=ASSETS/key;dest.parent.mkdir(parents=True,exist_ok=True)
        if not dest.exists() or dest.read_bytes()!=raw:dest.write_bytes(raw)

# Prepare minimal native QUESTS records matching the previously tested v0.51 schema.
catalog=[{k:q[k] for k in ('missionId','label','missionNameKey','dungeonId','requires',
                          'battles','exp','zel','karma','energy')} | {
    'dungeonNameKey':next(d['nameKey'] for d in dungeons if d['id']==q['dungeonId']),
    'background':next(d['background'] for d in dungeons if d['id']==q['dungeonId'])
    } for q in quests]
sourceview={'schema':m['schema'],
            'provenance':{'mastersZipSha256':p['mastersZipSha256'],
                          'missionMasterSha256':p['missionMasterSha256']},
            'dungeons':dungeons,
            'quests':[{'missionId':q['missionId'],'dungeonId':q['dungeonId'],
                       'name':q['name'],'description':q['description'],
                       'rawEncounterRef':q['rawEncounterRef'],
                       'rawAdditionalReward':q['rawAdditionalReward']} for q in quests]}
dump=lambda v:json.dumps(v,separators=(',',':'),ensure_ascii=True).replace('<',r'\u003c')
marker='/* BF_ORIGINAL_MORGAN_QUESTS_V080 */'
quests_js='window.BF_QUEST_CATALOG.push('+','.join(dump(row) for row in catalog)+');'
records_js='window.BF_MORGAN_QUEST_DATA_V080=Object.freeze('+dump(sourceview)+');'
bg_js=''.join('window.BF_QUEST_BACKGROUNDS['+dump(d['background'])+']='+dump('content/dungeon/'+d['background'])+';' for d in dungeons)
html=ASSETS/'index.html'
s=html.read_text('utf-8')
assert 'bf_global_offline_demo_v7' in s
assert s.count('/* BF_TOWER_OF_MISTRAL_V051 */')==1
assert s.count('window.BF_QUEST_BACKGROUNDS=')==1
assert s.count('window.BF_QUEST_BACKGROUNDS["dungeon_battle_10800.jpg"]')==1
if marker in s:
    assert s.count(marker)==s.count(quests_js)==s.count(records_js)==1
    assert s.count(bg_js)==1
    print('PASS v0.80 Morgan already staged, source exact')
else:
    assert s.count(marker)==s.count(quests_js)==s.count(records_js)==0
    s=s.replace('window.BF_QUEST_BACKGROUNDS=',marker+quests_js+records_js+
                'window.BF_QUEST_BACKGROUNDS=',1)
    old='window.BF_QUEST_BACKGROUNDS["dungeon_battle_10800.jpg"]="content/dungeon/dungeon_battle_10800.jpg";'
    assert s.count(old)==1
    s=s.replace(old,old+bg_js,1)
    html.write_text(s,'utf-8')
    print('PASS v0.80 36 source-authentic Morgan quests, 7 battle JPEGs, original area map, v7 unchanged')
