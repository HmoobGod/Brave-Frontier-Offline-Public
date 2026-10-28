"""Install nine verified owner 2022 Global Amdahl JPG/PNG assets into offline APK.

No 400-series playable quests, enemy waves, AI, save changes or fallback art.
"""
from pathlib import Path
from PIL import Image
import io,json,hashlib,zipfile,base64,gzip
R=Path(__file__).resolve().parent
M=json.loads((R/'source_data/bf_global_2022_amdahl_original_art_v149.json').read_text('utf8'))
Q=json.loads((R/'source_data/bf_global_2022_amdahl_quest_readiness_v147.json').read_text('utf8'))
Z=R/'source_assets/bf1/amdahl/BF1_Global_2022_Amdahl_Original_Art_v149.zip.b64'
A=R/'app/src/main/assets'
sha=lambda b:hashlib.sha256(b).hexdigest()
assert M['schema']=='bf-global-2022-amdahl-original-art-v149'
assert M['sourceArchiveSha256']=={
 'BF1_area_part001.zip':'17b7da1c4dc3e82a454571f5b4983e54ef95d1eff7eb19a808f1ea39ced98082',
 'BF1_dungeon_part001.zip':'a748f675fd8271c0f41bb0b9244c83ffc5d23b4051cfd757494d16735c506644'}
assert M['sourceMstSha256']==Q['provenance']['mstZipSha256']
assert M['sourceV147QuestCanonicalSha256']==Q['provenance']['questCanonSha256']
packed=base64.b64decode(Z.read_text('ascii'))
assert sha(packed)==M['packagedZipSha256']=='65790b0c0e9099fedb347e4a0c53f76bde7ebe3ea0cb7b9089557cf51c759179'
assert M['originalArea']=={'landId':3,'areaId':400,'image':'content/area/area_0004.jpg',
 'plate':'content/area/area_plate_0004.png','width':640,'height':960}
assert M['gameplayPolicy']=={'original2022QuestWavesDecoded':False,'playableQuests':False,'saveMutation':False}
coords=M['dungeons'];assert len(coords)==len(Q['dungeons'])==7
raw_source=base64.b64decode((R/'source_data/bf_global_2022_amdahl_raw_mst_v147.json.gz.b64').read_text('ascii'))
assert sha(raw_source)==Q['provenance']['rawCompressedSha256']
raw=json.loads(gzip.decompress(raw_source))
for d,m,original in zip(coords,Q['dungeons'],raw['dungeons']):
 assert d['id']==m['id']==int(original['missionDungeonId'])
 assert d['name']==m['name']
 assert d['battleBackground']==m['battleBackground']==original['missionBattleBackground']
 assert d['requires']==m['prerequisiteMissionId']==int(original['requiredMissionIds'])
 assert d['firstMissionId']==d['id']
 assert (d['x'],d['y'])==(int(original['QUEST_SnNtTh51']),int(original['QUEST_M6C1aXfR']))
 assert 0<=d['x']<=640 and 0<=d['y']<=960
assert len(M['sourceImages'])==9
assert set(M['sourceImages'])=={
 'content/area/area_0004.jpg','content/area/area_plate_0004.png',
 *(f'content/dungeon/dungeon_battle_{50100+100*i}.jpg' for i in range(7))}
with zipfile.ZipFile(io.BytesIO(packed)) as z:
 assert set(z.namelist())==set(M['sourceImages'])
 for path,info in M['sourceImages'].items():
  data=z.read(path)
  assert sha(data)==info['sha256'] and len(data)==info['bytes']
  assert info['sourcePack'] in M['sourceArchiveSha256']
  im=Image.open(io.BytesIO(data));im.verify()
  if path=='content/area/area_0004.jpg':
   assert Image.open(io.BytesIO(data)).size==(640,960)
  target=A/path
  target.parent.mkdir(exist_ok=True,parents=True)
  if target.is_file():assert target.read_bytes()==data,(path,'source asset conflict')
  else:target.write_bytes(data)
index=(A/'index.html').read_text('utf8')
assert 'bf_global_offline_demo_v7' in index
assert '/* BF_GLOBAL_AMDAHL_PLAYABLE_QUESTS_V147 */' not in index
print('PASS v149 owner original Amdahl world map + seven 2022 battle backgrounds, original coords + 106 quests/v7 saves untouched')
