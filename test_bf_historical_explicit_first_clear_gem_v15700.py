"""v157: independent 2015 Global explicit Gem metadata corroborates owner 2022 finale enum.

Research only. Neither 2015 source nor this test enables 2022 Gems, grants,
retrospective compensation, event rewards, or new save fields.
"""
from pathlib import Path
import hashlib,json,os,re
R=Path(__file__).resolve().parent
load=lambda path:json.loads((R/path).read_text('utf8'))
H=load('source_data/bf_global_2015_explicit_first_clear_gem_crosscheck_v157.json')
M=load('source_data/bf_global_2022_dungeon_finale_eligibility_v156.json')
E=load('source_data/bf_global_2022_first_clear_gem_source_v155.json')
assert H['schema']=='bf-global-2015-explicit-first-clear-gem-crosscheck-v157'
assert H['provenanceRepo']=='BluuArc/bfmt-data'
assert H['provenanceCommit']=='032f064db79c406fe4f027eb527085d09ea9b8af'
assert H['provenancePathTemplate']=='gl/mission/{missionId}.json'
assert H['sourceMetadataDate']=='2015-08-13T15:42:33.000Z'
assert H['sourceOriginal2022ZipSha256']==M['sourceZipSha256']==E['originalZipSha256']
assert H['original2022RewardPayload']=='8:0:1:0:0'
assert H['sourceKind'].startswith('historical 2015 Global')
assert H['columns']==['missionId','historicalGitBlobSha1','clearBonusKind','amount']
rows=H['rows']; controls=H['negativeControls']
assert len(rows)==H['corroboratedMissionCount']==29
assert len(controls)==8
assert hashlib.sha256(json.dumps(rows,separators=(',',':')).encode()).hexdigest()==H['canonicalRowsSha256']=='057df7d457aadfd9cf466113934e99db161979e2613403ab7afa9a707a1b8352'
assert rows==sorted(rows) and [r[0] for r in rows]==[r[0] for r in M['rows']]==[r[0] for r in E['rows']]
assert len({r[0] for r in rows})==29
assert all(r[2:]==['gem',1] and re.fullmatch('[a-f0-9]{40}',r[1]) for r in rows)
assert {r[0] for r in rows}.isdisjoint({r[0] for r in controls})
assert {r[0] for r in controls}=={1,11,20,203,300,364,400,403}
assert all(re.fullmatch('[a-f0-9]{40}',r[1]) for r in controls)
assert sum(q[4] for q in M['rows'])==H['currentlyPlayable']==22
assert len([q for q in M['rows'] if not q[4]])==H['amdahlSourceOnly']==7
assert all(r[1]=='8:0:1:0:0' for r in E['rows'])
assert not H['native2022WalletTransactionProven']
assert not H['native2022FirstClaimSemanticsProven']
assert not H['liveGemGrantsEnabled'] and not H['saveSchemaChanged']
assert not M['gemWalletMigrated'] and M['noLiveGemGrant']
# Optional *offline* verification of original Git blobs; no network in CI.
root=os.getenv('BF_HISTORICAL_2015_MISSION_DIR')
if root:
 root=Path(root)
 for mid,sha,_,_ in rows:
  raw=(root/f'{mid}.json').read_bytes()
  assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==sha,mid
  q=json.loads(raw)
  assert int(q['id'])==mid and q['clear_bonus']==[{'gem':'1'}]
  assert q['bfmtMetadata']['updatedAt']==H['sourceMetadataDate']
 for mid,sha in controls:
  raw=(root/f'{mid}.json').read_bytes()
  assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==sha,mid
  q=json.loads(raw)
  assert int(q['id'])==mid and q['clear_bonus']==[]
# Live original 2022 wallet still absent; do not substitute historical 2015 code.
html=(R/'app/src/main/assets/index.html').read_text('utf8')
save=html[html.index('const defaultProgress=()=>('):html.index('let P=defaultProgress()')]
assert 'version:7' in save and "questClears:{}" in save
assert 'gems:' not in save and 'out.gems=' not in save
assert 'bf_global_offline_demo_v7' in html
assert "applicationId 'org.bravefrontier.offline'" in (R/'app/build.gradle').read_text('utf8')
assert 'android.permission.INTERNET' not in (R/'app/src/main/AndroidManifest.xml').read_text('utf8')
print('PASS v157: 29 independent historical 2015 explicit Gem=1 finale rows / 8 non-finale negative controls; no 2022 Gem save or grant')
