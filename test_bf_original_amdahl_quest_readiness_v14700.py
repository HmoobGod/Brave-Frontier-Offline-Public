"""v147: exact owner 2022 Global Amdahl source readiness, no DEMO quests promoted."""
from pathlib import Path
import base64,gzip,hashlib,json
R=Path(__file__).resolve().parent
A=R/'app/src/main/assets'
D=R/'source_data'
meta=json.loads((D/'bf_global_2022_amdahl_quest_readiness_v147.json').read_text('utf8'))
P=meta['provenance']
sha=lambda data:hashlib.sha256(data).hexdigest()
assert meta['schema']=='bf-global-2022-amdahl-quest-readiness-v147'
assert P['mstZipSha256']=='69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9'
assert P['sgtextZipSha256']=='4dccce4eeb6a89cc0cf5718badff7af95046c891882e42c05c6eaca81f9d6285'
assert P['missionTableSha256']=='d4e364b6c1c5a825c0153c57bdd4123cd35800c74db795d913d119b6c9a99f83'
assert P['dungeonTableSha256']=='16f090514d65846f6bd4a9998b50d6c810bc806a79858c0ff766cdb1a22536fc'
packed=base64.b64decode((D/'bf_global_2022_amdahl_raw_mst_v147.json.gz.b64').read_text('ascii'))
assert sha(packed)==P['rawCompressedSha256']=='eb1d82bec0baa01fd6b217f2196dacc5086861192ece395fa3593e1499d4cb8e'
raw=gzip.decompress(packed)
assert sha(raw)==P['rawCanonicalSha256']=='758a2166fa728a3e11ce43c72ad11a18bba9dead78479c3ecef3d8354f041d1a'
source=json.loads(raw)
assert source['schema']=='bf-global-2022-amdahl-raw-mst-slice-v147'
assert source['sourceMissionTable'].endswith('F_MISSION_MST_1_Ver1118.json')
assert source['sourceDungeonTable'].endswith('F_DUNGEON_MST_Ver1002.json')
ids=[*range(400,405),*range(410,415),*range(420,425),*range(430,435),
     *range(440,445),*range(450,455),*range(460,466)]
assert len(ids)==36
qs=meta['quests'];old=source['missions'];dungeons=meta['dungeons']
assert [x['id'] for x in qs]==ids
assert [int(x['missionId']) for x in old]==ids
assert len(dungeons)==len(source['dungeons'])==7
assert [x['id'] for x in dungeons]==[400,410,420,430,440,450,460]
assert meta['area']=={'landId':3,'areaId':400,'name':'Amdahl',
       'priorAreaFinalMissionId':365,'missionCount':36,'dungeonCount':7,
       'originalEnemyWavesDecoded':False,'playableNow':False}
for i,(r,o) in enumerate(zip(qs,old)):
 mid=ids[i];prior=ids[i-1] if i else 365
 assert r['id']==int(o['missionId'])==mid
 assert r['prerequisiteMissionId']==int(o['requiredMissionIds'])==prior
 assert r['dungeonId']==int(o['missionDungeonId'])
 assert (o['missionLandId'],o['missionAreaId'])==('3','400')
 assert o['missionNpcId']=='0'
 assert r['waveCount']==int(o['missionBattleCount']) and r['waveCount']>0
 for key,mst_key in [('energy','missionEnergyUse'),('exp','exp'),('zel','zel'),('karma','karma')]:
  assert r[key]==int(o[mst_key]) and r[key]>=0
 assert r['rawEncounterRef']==o['MISSION_8f4NYKxb']
 assert r['battleMusic']==o['missionBattleMusic'] and r['bossMusic']==o['missionBossBattleMusic']
 assert r['rawRewards']==o['missionRewards']
 namekey=f'MST_DUNGEONS_MISSION_{mid}_NAME'
 desckey=f'MST_DUNGEONS_MISSION_{mid}_DESCRIPTION'
 assert o['missionName']==namekey and o['description']==desckey
 assert r['name']==source['sourceEnglish'][namekey] and r['name']
 assert r['description']==source['sourceEnglish'][desckey] and r['description']
for d,o in zip(dungeons,source['dungeons']):
 assert d['id']==int(o['missionDungeonId'])
 assert d['nameSourceKey']==o['dungeonName']
 assert d['areaId']==int(o['missionAreaId'])==400
 assert d['landId']==int(o['missionLandId'])==3
 assert d['prerequisiteMissionId']==int(o['requiredMissionIds'])
 assert d['battleBackground']==o['missionBattleBackground']
 assert d['name'] and d['battleBackground']==f'dungeon_battle_{50100+100*((d["id"]-400)//10)}.jpg'
canon=json.dumps([[r[k] for k in ('id','dungeonId','prerequisiteMissionId','waveCount',
 'energy','exp','zel','karma','rawEncounterRef','battleMusic','bossMusic')] for r in qs],
 ensure_ascii=False,separators=(',',':')).encode('utf8')
assert sha(canon)==P['questCanonSha256']=='f35a7b06bc9e6fae6facc1fd77422f74c04798da4fb87f64a2737a0483a572c3'
assert qs[0]['id']==400 and qs[0]['name']=='The Scars of War' and qs[0]['energy']==10
assert qs[-1]['id']==465 and qs[-1]['energy']==17 and qs[-1]['exp']==3000
html=(A/'index.html').read_text('utf8')
assert 'bf_global_offline_demo_v7' in html
assert '/* BF_GLOBAL_AMDAHL_PLAYABLE_QUESTS_V147 */' not in html
assert not (A/'bf14700_amdahl_playable.js').exists()
print('PASS v147: 36 original Global Amdahl missions, 7 dungeons, exact English names/prerequisites/rewards/energy/music and no save or gameplay promotion')
