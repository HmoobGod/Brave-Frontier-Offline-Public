"""v0.90 source-backend St. Lamia region, 36 English Global quests and art.

Original 2022 names, wave counts, unlocks, metadata, battle JPGs and world map.
Native enemy waves, drops, AI, damage formulas and sound are NOT reconstructed.
Save version and existing player progress remain unchanged.
"""
from pathlib import Path
from zipfile import ZipFile
import hashlib,json

R=Path(__file__).resolve().parent
A=R/'app/src/main/assets'
S=R/'source_assets/bf1/stlamia'
def sha(b):return hashlib.sha256(b).hexdigest()
bundle=S/'StLamia_2022_Source_Dataset_v090.zip'
with ZipFile(bundle) as z:
    assert z.namelist()==['source_data/bf_global_st_lamia_original_v090.json']
    m=json.loads(z.read(z.namelist()[0]))
assert m['schema']=='bf-global-st-lamia-2022-original-quests-v090'
p=m['provenance']
assert p['mastersZipSha256']=='69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9'
assert p['missionMasterSha256']=='d4e364b6c1c5a825c0153c57bdd4123cd35800c74db795d913d119b6c9a99f83'
assert p['dungeonMasterSha256']=='16f090514d65846f6bd4a9998b50d6c810bc806a79858c0ff766cdb1a22536fc'
assert p['languageZipSha256']=='4dccce4eeb6a89cc0cf5718badff7af95046c891882e42c05c6eaca81f9d6285'
assert len(m['dungeons'])==7 and len(m['quests'])==36
dids=[300,310,320,330,340,350,360]
ids=[*range(300,305),*range(310,315),*range(320,325),*range(330,335),
     *range(340,345),*range(350,355),*range(360,366)]
assert [x['id'] for x in m['dungeons']]==dids
assert [x['missionId'] for x in m['quests']]==ids
assert all(x['requires']==(ids[i-1] if i else 265) for i,x in enumerate(m['quests']))
assert all(x['areaId']==300 and x['landId']==1 and
           x['nameKey']==f"MST_DUNGEONS_DUNGEON_{x['id']}_NAME" for x in m['dungeons'])
assert all(x['name'] and x['description'] and x['battles']>0 and x['exp']>=0 and
           x['zel']>=0 and x['karma']>=0 for x in m['quests'])
for typ,filename in [('art','StLamia_2022_Original_Battle_Backgrounds.zip'),
                     ('world','StLamia_2022_Original_World_Map.zip')]:
    path=S/filename
    assert sha(path.read_bytes())==p['artBundleSha256' if typ=='art' else 'worldMapBundleSha256']
    with ZipFile(path) as z:
        if typ=='art':
            assert set(z.namelist())=={'content/dungeon/'+x['background'] for x in m['dungeons']}
            for d in m['dungeons']:
                dest='content/dungeon/'+d['background']
                data=z.read(dest)
                assert len(data)==d['imageBytes'] and sha(data)==d['imageSha256']
                assert data[:3]==bytes((255,216,255))
                target=A/dest;target.parent.mkdir(parents=True,exist_ok=True)
                if not target.is_file() or target.read_bytes()!=data:target.write_bytes(data)
        else:
            assert set(z.namelist())==set(p['worldFiles'])
            for dest,meta in p['worldFiles'].items():
                data=z.read(dest)
                assert len(data)==meta['bytes'] and sha(data)==meta['sha256']
                target=A/dest;target.parent.mkdir(parents=True,exist_ok=True)
                if not target.is_file() or target.read_bytes()!=data:target.write_bytes(data)

catalog=[]
for q in m['quests']:
    dungeon=next(x for x in m['dungeons'] if x['id']==q['dungeonId'])
    info={k:q[k] for k in ('missionId','label','missionNameKey','dungeonId','requires',
                           'battles','energy','exp','zel','karma')}
    info['dungeonNameKey']=dungeon['nameKey']
    info['background']=dungeon['background']
    catalog.append(info)
records={'schema':m['schema'],
         'provenance':{'missionMasterSha256':p['missionMasterSha256']},
         'dungeons':m['dungeons'],
         'quests':[{'missionId':q['missionId'],'dungeonId':q['dungeonId'],
                    'name':q['name'],'description':q['description']} for q in m['quests']]}
dump=lambda o:json.dumps(o,separators=(',',':'),ensure_ascii=True).replace('<',r'\u003c')
append='window.BF_QUEST_CATALOG.push('+','.join(dump(q) for q in catalog)+');'
reference='window.BF_STLAMIA_QUEST_DATA_V090=Object.freeze('+dump(records)+');'
bg=''.join('window.BF_QUEST_BACKGROUNDS['+dump(d['background'])+']='+dump('content/dungeon/'+d['background'])+';' for d in m['dungeons'])
f=A/'index.html';s=f.read_text('utf8')
assert 'bf_global_offline_demo_v7' in s
assert '/* BF_ORIGINAL_MORGAN_QUESTS_V080 */' in s
marker='/* BF_STLAMIA_QUESTS_V090 */';bgmarker='/* BF_STLAMIA_BACKGROUNDS_V090 */'
if marker in s:
    assert s.count(marker)==s.count(bgmarker)==1
    assert s.count(reference)==s.count(append)==s.count(bg)==1
    print('PASS v0.90 St. Lamia sources already staged')
else:
    assert s.count(marker)==s.count(bgmarker)==0
    assert s.count('window.BF_QUEST_BACKGROUNDS=')==1
    s=s.replace('window.BF_QUEST_BACKGROUNDS=',marker+append+reference+'window.BF_QUEST_BACKGROUNDS=',1)
    anchor='window.BF_QUEST_BACKGROUNDS["dungeon_battle_20700.jpg"]="content/dungeon/dungeon_battle_20700.jpg";'
    assert s.count(anchor)==1
    s=s.replace(anchor,anchor+bgmarker+bg,1)
    f.write_text(s,'utf8')
    print('PASS v0.90 St. Lamia 36 original quests, seven original battle images/world map, unchanged v7')
