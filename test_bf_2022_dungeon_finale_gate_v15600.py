"""v156: original 2022 dungeon-finale first-clear reward eligibility, NO Gem grant.

A source-backed safety gate for future native first-clear reward work.
"""
from pathlib import Path
from collections import defaultdict
import hashlib,json,os,zipfile
R=Path(__file__).resolve().parent
read=lambda p:json.loads((R/p).read_text('utf8'))
M=read('source_data/bf_global_2022_dungeon_finale_eligibility_v156.json')
v155=read('source_data/bf_global_2022_first_clear_gem_source_v155.json')
v142=read('source_data/bf_global_original_2022_live_quest_economy_v142.json')
amd=read('source_data/bf_global_2022_amdahl_quest_readiness_v147.json')
canon=lambda v:hashlib.sha256(json.dumps(v,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
assert M['schema']=='bf-global-original-2022-final-dungeon-first-clear-gate-v156'
assert M['sourceZipSha256']==v155['originalZipSha256']==v142['sourceArchiveSha256']=='69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9'
assert M['originalMissionMasterSha256']==v142['missionMasterSha256']==v155['sourceTables'][0]['sha256']=='d4e364b6c1c5a825c0153c57bdd4123cd35800c74db795d913d119b6c9a99f83'
assert M['v155CanonicalRewardRowsSha256']==v155['sourceRowsSha256']=='de8bde1cbee451e3c1b07c8b3e47afd38bc0465787b2b4aa6f5c8a620c4c83a7'
assert M['columns']==['missionId','dungeonId','requiredPreviousMissionId','missionCountInDungeon','liveIn106Quests']
rows=M['rows']
assert len(rows)==M['originalRewardFinales']==29
assert len({row[0] for row in rows})==len({row[1] for row in rows})==29
assert rows==sorted(rows)
assert canon(rows)==M['canonicalRowsSha256']=='0086bcd4f08b1fc6a748c800f5444221afbb1c1a6fc749e9c7e593111498b3c8'
assert sum(x[4] for x in rows)==M['currentPlayableFinales']==22
assert sum(not x[4] for x in rows)==M['amdahlUnplayableFinales']==7
assert M['sourceMissionCount']==142
assert M['allFinalePrerequisitesDirect'] is True
assert M['noLiveGemGrant'] is True and M['gemWalletMigrated'] is False
assert [row[0] for row in rows]==[row[0] for row in v155['rows']]
assert all(row[4]==v155['rows'][i][2] and v155['rows'][i][1]=='8:0:1:0:0'
           for i,row in enumerate(rows))
live={x[0]:(x[1],x[2]) for x in v142['records']}
source_only={x['id']:(x['dungeonId'],x['prerequisiteMissionId']) for x in amd['quests']}
assert len(live)==v142['total']==106
assert len(source_only)==36
assert not (set(live)&set(source_only))
assert amd['area']['playableNow'] is False
by_dungeon=defaultdict(list)
for id,(d,req) in {**live,**source_only}.items():by_dungeon[d].append((id,req))
assert sum(len(a) for a in by_dungeon.values())==142
for id,d,req,n,playable in rows:
 assert isinstance(id,int) and isinstance(d,int) and isinstance(req,int) and isinstance(n,int)
 assert req>0 and n>=3 and n<=6
 assert (id in live)==bool(playable)
 assert (d,req)==(live if playable else source_only)[id]
 chain=sorted(by_dungeon[d])
 assert len(chain)==n
 assert id==chain[-1][0],(id,d,chain)
 assert req==chain[-2][0],(id,d,chain)
 assert chain[-1][1]==req
assert [row[0] for row in rows if not row[4]]==[404,414,424,434,444,454,465]

# Replay and saved-progress eligibility cannot be inferred from the source
# records alone. Document the exact still-blocking current save behavior.
html=(R/'app/src/main/assets/index.html').read_text('utf8')
start=html.index('const defaultProgress=()=>(')
end=html.index('let P=defaultProgress()',start)
save_source=html[start:end]
assert "version:7" in save_source
assert "questClears:{}" in save_source
assert "return out;" in save_source
assert 'function parseProgress(data)' in save_source
assert "for(const key of ['exp','zel','karma','clears'])" in save_source
assert 'out.questClears[id]=limitNumber(count)' in save_source
assert 'gems:' not in save_source and 'out.gems=' not in save_source
assert "const SAVE_KEY='bf_global_offline_demo_v7'" in html
assert 'P.questClears[QUEST.missionId]=(P.questClears[QUEST.missionId]||0)+1' in html
assert 'P.gems+=' not in html
assert 'bf15500_first_clear_gem_source.js' in (R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert "applicationId 'org.bravefrontier.offline'" in (R/'app/build.gradle').read_text('utf8')
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')

# Optional exact original ZIP regeneration; source archive is NOT committed.
archive=os.environ.get('BF_ORIGINAL_2022_MST_ZIP')
if archive:
 p=Path(archive)
 assert hashlib.sha256(p.read_bytes()).hexdigest()==M['sourceZipSha256']
 with zipfile.ZipFile(p) as z:
  raw=z.read(M['originalMissionMasterPath'])
  assert hashlib.sha256(raw).hexdigest()==M['originalMissionMasterSha256']
  allM=json.loads(raw)
  ids={q[0] for q in rows}
  grouped=defaultdict(list)
  for q in allM:
   try:mission_id=int(q['missionId']);dungeon_id=int(q['missionDungeonId'])
   except (KeyError,ValueError,TypeError):continue
   grouped[dungeon_id].append(q)
  regenerated=[]
  for mid,d,req,n,playable in rows:
   sub=sorted(grouped[d],key=lambda q:int(q['missionId']))
   final=sub[-1]
   assert int(final['missionId'])==mid and final['missionRewards']=='8:0:1:0:0'
   assert int(final['requiredMissionIds'])==int(sub[-2]['missionId'])==req
   regenerated.append([mid,d,req,len(sub),playable])
  assert regenerated==rows
print('PASS v156: 29/29 2022 source dungeon finales with direct preceding prereqs, 22 live/7 Amdahl source-only; strict v7 Gem-wallet blocker')
