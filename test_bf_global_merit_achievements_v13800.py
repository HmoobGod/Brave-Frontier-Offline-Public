"""v138: strictly read-only original 2022 Global Merit challenge evidence.
No achievement auto-claim, no new save fields and no expired challenge revival.
"""
from pathlib import Path
from collections import Counter
import base64, gzip, hashlib, json
R=Path(__file__).resolve().parent
A=R/'app/src/main/assets'
M=json.loads((R/'source_data/bf_global_2022_merit_achievement_v138.json').read_text('utf8'))
assert M['schema']=='bf-global-2022-permanent-merit-achievement-evidence-v138'
assert M['sourceArchiveSha256']=='69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9'
assert M['sourceFiles']==[
 {'path':'3-mst-translated/F_ACHIEVEMENT_SUBJECT_MST_1_Ver503.json','sha256':'36850eac317faf97f6196d8078b56d8a2594847eb2a727917b0d1bd1485efb56','rows':5058},
 {'path':'3-mst-translated/F_ACHIEVEMENT_SUBJECT_MST_2_Ver503.json','sha256':'4978d0dc242306e02562b270c545bd6423811a66b909586e11d5990bdd0be2aa','rows':5058},
 {'path':'3-mst-translated/F_ACHIEVEMENT_SUBJECT_MST_3_Ver503.json','sha256':'5ff71a93b91da7ef171820a7efa401e62076f755b1aa1b8cffc0bccf01c56c0f','rows':5057}]
assert M['originalRows']==sum(z['rows'] for z in M['sourceFiles'])==15173
assert M['rowsWithNonexpiredPositiveMerit']==657
assert M['rawTupleColumns']==[
 'sourcePart','achievementSubjectId','achievementSubjectName','description',
 'achievmentType','originalRequirementParameter','meritPointReward','availabilityTimeEnd']
packed=base64.b64decode(M['gzipBase64'],validate=True)
assert len(packed)==M['gzipBytes']==12068
assert hashlib.sha256(packed).hexdigest()==M['gzipSha256']
raw=gzip.decompress(packed)
assert len(raw)==M['rawTupleBytes']==85666
assert hashlib.sha256(raw).hexdigest()==M['rawTupleSha256']=='bf708759dc3d57ade12980bf72569e407889f476817938790b85259d2cc9ca22'
rows=json.loads(raw)
assert len(rows)==657 and len({r[1] for r in rows})==657
assert rows==sorted(rows,key=lambda r:(r[0],r[1]))
assert all(len(r)==8 and r[0] in (1,2,3) and isinstance(r[1],int) and
           isinstance(r[4],int) and isinstance(r[6],int) and r[6]>0 and
           r[7]=='9999-12-31 23:59:59' for r in rows)
ct=Counter(str(r[4]) for r in rows)
assert dict(sorted(ct.items(),key=lambda z:int(z[0])))==M['typeCounts']
assert ct['100']==12 and ct['700']==12 and ct['8500']==14 and ct['5400']==16
for key in M['selectedExamples']:
 assert [ [r[1],r[2],r[5],r[6]] for r in rows if str(r[4])==key][:8]==M['selectedExamples'][key]
assert [r[6] for r in rows if r[1] in (1000,1010,1020)]==[100,200,400]
assert [r[6] for r in rows if r[1] in (3000,3010,3020)]==[100,500,1000]
assert [r[6] for r in rows if r[1] in (34000,34010,34020)]==[100,200,400]
assert [r[6] for r in rows if r[1] in (24000,24010,24020)]==[100,200,400]
assert M['researchOnly'] is True and M['liveGrantEnabled'] is False
assert M['expiryGuaranteeProven'] is False and M['conditionDecodingProven'] is False
html=(A/'index.html').read_text('utf8')
assert 'bf_global_offline_demo_v7' in html
assert not (A/'bf13800_merit_awards.js').exists()
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf8')
assert 'bf13800_merit_awards.js' not in java
print('PASS v138: 657 original nonexpiring Merit achievement references, 15,173 source rows, immutable 2022 rewards; no live claims or v7 save changes')
