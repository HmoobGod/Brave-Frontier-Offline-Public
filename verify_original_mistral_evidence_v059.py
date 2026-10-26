"""v0.59: verify archived Global mission-reference fixtures without decoding unknown mechanics.

Source: exact 2022 translated F_MISSION_MST_1_Ver1118.json (SHA256
d4e364b6c1c5a825c0153c57bdd4123cd35800c74db795d913d119b6c9a99f83).
Never turn opaque master data into guessed enemy IDs, native rewards or mimic odds.
"""
from pathlib import Path
import hashlib,json,re

ROOT=Path(__file__).resolve().parent
path=ROOT/'source_data/bf_global_mistral_raw_mission_evidence_v056.json'
m=json.loads(path.read_text('utf-8'))
assert m['schema']=='bf-global-2022-mistral-raw-mission-evidence-v056'
assert m['source']['archiveSha256']=='69c3d919903039d8e8bdfb3327909b7177ae358d177b59db254980c6233776a9'
assert m['source']['fileSha256']=='d4e364b6c1c5a825c0153c57bdd4123cd35800c74db795d913d119b6c9a99f83'
assert m['source']['columns']==['missionId','MISSION_8f4NYKxb','missionMimicInfo','missionRewards','cutsceneFile','missionNpcId']
rows=m['rows']
ids=[1,2,10,11,12,20,21,22,23,30,31,32,33,40,41,42,43,
     50,51,52,53,60,61,62,63,70,71,72,73,81,82,83,84,85]
assert [r['missionId'] for r in rows]==ids
refs={
    (1,2,10,11,12):'3:10100,1:10101,0:10102',
    (20,21,22,23):'3:10200,1:10201,0:10202',
    (30,31,32,33):'3:10300,1:10301',
    (40,41,42,43):'3:10400,1:10402',
    (50,51,52,53):'3:10500,1:10501,0:10502',
    (60,61,62,63):'1:10600',
    (70,71,72,73):'3:10400,2:10701,1:10702,0:10703',
    (81,82,83,84,85):'1:10800,0:10801'
}
lookup={j:v for key,v in refs.items() for j in key}
assert set(lookup)==set(ids)
special_reward={12,23,33,43,53,63,73,85}
cutscenes={10:'0,map1-dungeon0-1end.txt',11:'0,map1-dungeon0-2end.txt',
           21:'0,map1-dungeon0-3end.txt'}
for row in rows:
    id=row['missionId']
    assert row['rawEncounterRef']==lookup[id],id
    assert re.fullmatch(r'[0-9]+:[0-9]+(?:,[0-9]+:[0-9]+)*',row['rawEncounterRef'])
    assert row['rawMimicInfo']==(
        '0,0,0:0,0:0' if id<=53 else '1,10,100:1000,0:0')
    assert row['rawRewards']==('8:0:1:0:0' if id in special_reward else '')
    assert row['rawCutscene']==cutscenes.get(id,'0,0')
    assert row['rawMissionNpcId']=='0'
assert len(special_reward)==8 and len(cutscenes)==3
assert len(m['source']['limitations'])==4
print('PASS v0.59: 34 source-exact opaque encounter fields, 8 reward tokens, 3 cutscene filenames, no fabricated IDs')
