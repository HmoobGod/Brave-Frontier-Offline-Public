"""v152: original 2022 encounter reference reuse across ordinary, Grand, Raid mission tables.

Research-only. Shared opaque strings, backdrop coincidences and mission wave counts
DO NOT reconstruct enemy IDs, native wave layouts, AI or loot.
"""
from pathlib import Path
from collections import Counter
import base64,gzip,hashlib,json,os,re,zipfile

R=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
packed=base64.b64decode((R/'source_data/bf_global_2022_mission_cross_table_v152.json.gz.b64').read_text('ascii'),validate=True)
assert sha(packed)=='cc8aeda4a3f95555985bf4aada5c75f1f1dfdb67f0ee800d36b7aba56327f59a'
raw=gzip.decompress(packed)
assert sha(raw)=='2f5daf4b5c74fcc53965f1115e5e1ce37bf788f03e372900f57bb1bd9843f2f7'
v=json.loads(raw)
assert v['schema']=='bf-global-original-2022-142-mission-cross-table-evidence-v152'
assert v['sourceZipSha256']=='69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9'
assert v['columns']==['missionId','opaqueEncounterField','dungeonBackdrop','matchingGrandSpotRows','matchingRaidPointRows']
rows=v['rows']
assert len(rows)==142 and len({r[0] for r in rows})==142
assert sha(json.dumps(rows,separators=(',',':'),ensure_ascii=False).encode())==v['canonicalRowsSha256']=='2acd1ab29b8a00b3c8804a89fdc9d7b99cba4853f5974f765bc7473c89e7a284'
assert all(len(r)==5 and type(r[0]) is int and type(r[3]) is int and type(r[4]) is int and
           r[3]>=0 and r[4]>=0 and
           re.fullmatch(r'\d+:\d+(?:,\d+:\d+)*',r[1]) and
           re.fullmatch(r'dungeon_battle_\d+\.jpg',r[2]) for r in rows)
assert sum(r[3]>0 for r in rows)==92
assert sum(r[4]>0 for r in rows)==99
assert sum(r[3]>0 and r[4]>0 for r in rows)==73
same=[r[0] for r in rows if r[2]==f"dungeon_battle_{r[1].split(',')[0].split(':')[1]}.jpg"]
diff=[r[0] for r in rows if r[0] not in same]
assert len(same)==133 and diff==[70,71,72,73,230,231,232,233,234]
assert len({part.split(':')[1] for row in rows for part in row[1].split(',')})==58
live=json.loads((R/'source_data/bf_global_original_2022_live_quest_economy_v142.json').read_text('utf8'))
mistral=json.loads((R/'source_data/bf_global_mistral_raw_mission_evidence_v056.json').read_text('utf8'))
morgan=json.loads((R/'source_data/bf_global_morgan_original_v080.json').read_text('utf8'))
st=json.loads((R/'source_data/bf_global_st_lamia_raw_encounter_refs_v109.json').read_text('utf8'))
amd=json.loads((R/'source_data/bf_global_2022_amdahl_quest_readiness_v147.json').read_text('utf8'))
amd_art=json.loads((R/'source_data/bf_global_2022_amdahl_original_art_v149.json').read_text('utf8'))
assert live['total']==106 and len(live['records'])==106
assert amd['area']['missionCount']==36 and amd['area']['playableNow'] is False
assert amd['area']['originalEnemyWavesDecoded'] is False
assert st['provenance']['masterSha256']==live['missionMasterSha256']==amd['provenance']['missionTableSha256']
lookup={r[0]:r for r in rows}
assert set(lookup)=={r[0] for r in live['records']}|{q['id'] for q in amd['quests']}
ref={}
for array,idkey in ((mistral['rows'],'missionId'),(morgan['quests'],'missionId'),(st['rows'],'missionId'),(amd['quests'],'id')):
 for q in array:
  assert q[idkey] not in ref
  ref[q[idkey]]=q['rawEncounterRef']
assert len(ref)==142 and all(lookup[k][1]==value for k,value in ref.items())
assert [r[0] for r in rows[:106]]==[r[0] for r in live['records']]
assert [r[0] for r in rows[106:]]==[q['id'] for q in amd['quests']]
for q in amd['quests']:
 assert lookup[q['id']][0]==q['id']
 matched=[d for d in amd_art['dungeons'] if d['id']==q['dungeonId']]
 assert len(matched)==1 and lookup[q['id']][2]==matched[0]['battleBackground']
assert len([r for r in rows if 400<=r[0]<=465])==36
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
html=(R/'app/src/main/assets/index.html').read_text('utf8')
assert 'bf_global_offline_demo_v7' in html
assert 'bf15200' not in java and 'bf15200' not in html
assert 'P.version' in html
assert "applicationId 'org.bravefrontier.offline'" in (R/'app/build.gradle').read_text('utf8')
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')

# Local provenance regeneration on the exact original archive; CI is self-contained.
if os.environ.get('BF_ORIGINAL_2022_MST_ZIP'):
 path=Path(os.environ['BF_ORIGINAL_2022_MST_ZIP'])
 assert sha(path.read_bytes())==v['sourceZipSha256']
 with zipfile.ZipFile(path) as z:
  def read(name,expected):
   data=z.read('3-mst-translated/'+name)
   assert sha(data)==expected,(name,sha(data))
   return json.loads(data)
  original=read('F_MISSION_MST_1_Ver1118.json','d4e364b6c1c5a825c0153c57bdd4123cd35800c74db795d913d119b6c9a99f83')
  dungeon=read('F_DUNGEON_MST_Ver1002.json','16f090514d65846f6bd4a9998b50d6c810bc806a79858c0ff766cdb1a22536fc')
  grand=read('F_GRAND_MISSION_SPOT_MST_Ver92.json','ce9ac03cc8e1eb877d3afe6855336b2c7a6fe0b085cd75aed0a350bad7552eb5')
  raid=read('F_RAID_POINT_MST_Ver57.json','62433315a048dc83f50b4711ce633085ab76672ae6c5260e0f3b6445a2587009')
  original={int(x['missionId']):x for x in original if x.get('missionId','').isdigit()}
  backgrounds={int(x['missionDungeonId']):x.get('missionBattleBackground') for x in dungeon if x.get('missionDungeonId','').isdigit()}
  g=Counter(x.get('MISSION_8f4NYKxb') for x in grand if x.get('MISSION_8f4NYKxb'))
  a=Counter(x.get('MISSION_8f4NYKxb') for x in raid if x.get('MISSION_8f4NYKxb'))
  generated=[]
  for id in lookup:
   m=original[id];group=m['MISSION_8f4NYKxb']
   generated.append([id,group,backgrounds[int(m['missionDungeonId'])],g.get(group,0),a.get(group,0)])
  assert generated==rows,[(got,want) for got,want in zip(generated,rows) if got!=want][:5]
print('PASS v152: 142 original 2022 mission references, Grand/Raid reuse 92/99 (73 shared), 133 source backdrop joins; 9 exceptions, no gameplay/save changes')
