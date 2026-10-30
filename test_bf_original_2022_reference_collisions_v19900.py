"""v199 read-only authenticated 2022 mission reference collision regression."""
from copy import deepcopy
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import tempfile

import audit_bf_original_2022_reference_collisions_v19900 as audit

ROOT=Path(__file__).resolve().parent
FILES=[
 ROOT/'source_data'/entry[0] for entry in audit.SOURCES.values()
]+[
 ROOT/'source_data/bf_global_2022_mission_cross_table_v152.json.gz.b64',
 ROOT/'app/src/main/assets/index.html',
 ROOT/'app/src/main/java/org/bravefrontier/offline/MainActivity.java',
 ROOT/'app/build.gradle',
]
existing={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in FILES}
rows=audit.read_original()
assert len(rows)==142
report=audit.analyze(rows)
assert report==audit.compare()
assert report['schema']=='bf-global-v199-2022-opaque-encounter-reference-collisions'
assert report['sourceArchiveSha256']==audit.ZIP2022
assert report['sourceMissionMasterSha256']==audit.MASTER2022
assert report['missionCount']==142
assert report['distinctRawReferenceStrings']==29
assert report['missionsSharingSomeRawReference']==142
assert report['sourceAreas']=={'mistral':34,'morgan':36,'stlamia':36,'amdahl':36}
assert report['referenceReuseSizeHistogram']=={'4':6,'5':20,'6':3}
assert report['crossAreaExactReuseGroups']==0
assert report['rawTokenPairCountBuckets']=={
    'one':31,'two':84,'threeOrMore':27}
assert all(report[x] is False for x in (
 'native2022EnemyIdsVerified','native2022WaveFormationsVerified',
 'native2022EncounterWeightsVerified','native2022EnemyAIAndDropsVerified',
 'changesGameplay','changesSaves','changesAndroid'))

def reject(modifier):
    bad=deepcopy(rows)
    modifier(bad)
    try:
        audit.analyze(bad)
    except (AssertionError, ValueError, TypeError):
        return
    raise AssertionError('Source mutation accepted: '+modifier.__name__)

def bad_duplicate(data):data[1]['missionId']=data[0]['missionId']
def bad_malformed(data):data[0]['rawEncounterRef']='3:100,0:broken'
def bad_trailing_comma(data):data[0]['rawEncounterRef']+=','
def bad_reinterpret_group(data):data[0]['rawEncounterRef']='this-is-a-formation'
def bad_wrong_area(data):data[0]['area']='amdahl'
def bad_missing_mission(data):data.pop()
def bad_new_ref(data):data[0]['rawEncounterRef']='9999:8888'
def bad_ref_type(data):data[0]['rawEncounterRef']=['3:10100']
def bad_unexpected_key(data):data[0]['enemyUnitId']=1234
for fn in (bad_duplicate,bad_malformed,bad_trailing_comma,
           bad_reinterpret_group,bad_wrong_area,bad_missing_mission,
           bad_new_ref,bad_ref_type,bad_unexpected_key):
    reject(fn)

with tempfile.TemporaryDirectory() as tmp:
    report_file=Path(tmp)/'2022-reference-collisions.json'
    command=[sys.executable,str(ROOT/'audit_bf_original_2022_reference_collisions_v19900.py'),
             '--output',str(report_file)]
    subprocess.run(command,cwd=ROOT,check=True,capture_output=True,text=True)
    assert json.loads(report_file.read_text('utf8'))==report
    before=report_file.read_bytes()
    subprocess.run(command,cwd=ROOT,check=True,capture_output=True,text=True)
    assert before==report_file.read_bytes()
blocked=subprocess.run([
 sys.executable,str(ROOT/'audit_bf_original_2022_reference_collisions_v19900.py'),
 '--output',str(ROOT/'forbidden-v199.json')],cwd=ROOT,capture_output=True,text=True)
assert blocked.returncode!=0
assert not (ROOT/'forbidden-v199.json').exists()
assert {str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in FILES}==existing
assert "applicationId 'org.bravefrontier.offline'" in (ROOT/'app/build.gradle').read_text('utf8')
assert 'bf_global_offline_demo_v7' in (ROOT/'app/src/main/assets/index.html').read_text('utf8')
print('PASS v199: 142 missions, 29 reused opaque refs; 9 corruption probes, deterministic research and no game/save changes')
