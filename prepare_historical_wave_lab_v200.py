"""Build source-attributed offline 2014 historical quest research, never native 2022 combat.
No network accesses. Immutable upstream Git blob IDs are retained for every row.
Idempotently fill a separate Android WebView JS asset with compact, inert JSON.
"""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parent
A=ROOT/'app/src/main/assets'
D=ROOT/'source_data'
old=json.loads((D/'bf_global_historical_encounters_v120.json').read_text('utf8'))['missions']
new=[json.loads(p.read_text('utf8')) for p in sorted(
    (D/'historical_2014_v200').glob('mission_*.json'))]
assert len(old)==4 and len(new)==17, (len(old),len(new))
rows=sorted(old+new,key=lambda x:x['id'])
ids=[1,2,10,11,20,21,30,31,40,41,42,50,51,52,60,61,70,71,200,202,240]
assert [m['id'] for m in rows]==ids
assert all(isinstance(m['name'],str) and m['name'] and
    m['sourcePath'].startswith('missions_parsed/') and
    len(m['gitBlobSha'])==40 and
    all(c in '0123456789abcdef' for c in m['gitBlobSha']) and
    m['waves'] and all(w['wave']==i+1 and w['enemies'] for i,w in
    enumerate(m['waves'])) for m in rows)
enemies=[e for m in rows for w in m['waves'] for e in w['enemies']]
assert all(isinstance(e['name'],str) and e['name'] and
    all(type(e[k]) is int and e[k]>=0 for k in
        ('unitId','hp','atk','def','aiId')) for e in enemies)
totals={'missions':len(rows),'waves':sum(len(m['waves']) for m in rows),
        'entries':len(enemies),'units':len({e['unitId'] for e in enemies})}
assert totals=={'missions':21,'waves':112,'entries':264,'units':42},totals
# v411: Validate two independently observed 2014 Mission #10 captures.
# The alternate differs only at wave 4. Never infer original 2022 waves.
alt=json.loads((D/'bf_mission10_dual_2014_capture_v411.json').read_text('utf8'))
m10=next(m for m in old if m['id']==10)
assert alt['schema']=='bf-global-mission10-dual-2014-capture-v411'
assert alt['sourceEra']==2014 and alt['missionId']==10 and alt['missionName']==m10['name']
assert alt['historicalPracticeOnly'] is True
assert alt['native2022FormationsVerified'] is False
assert alt['native2022EnemyAIAndDropsVerified'] is False
assert alt['originalGameRewardsEnabled'] is False
assert alt['primary']=={
 'sourcePath':m10['sourcePath'],'gitBlobSha':m10['gitBlobSha']}
assert alt['alternate']['sourcePath']=='missions_parsed/Start of Adventure_2014-14-10-08-34.json'
assert alt['alternate']['gitBlobSha']=='c6a9d86b7e72a079ebdaa48b84864d078e5568e3'
assert alt['waves']==len(m10['waves'])==5 and alt['enemySlots']==11
assert alt['identicalOtherWaves']==[1,2,3,5] and alt['onlyChangedWave']==4
assert m10['waves'][3]['enemies']==alt['wave4Original']
assert [e['name'] for e in alt['wave4Alternate']]==['Burny','Glowy','Mossy']
assert [e['unitId'] for e in alt['wave4Alternate']]==[10030,50030,30030]
assert [e['hp'] for e in alt['wave4Alternate']]==[800,850,830]
assert [e['atk'] for e in alt['wave4Alternate']]==[320,340,340]
assert [e['def'] for e in alt['wave4Alternate']]==[50,60,90]
assert all(e['aiId']==1 for e in alt['wave4Alternate'])
assert alt['observations']['bothHaveOneNormalAttackPerEnemy'] is True
# v413: A second, independently pinned original 2014 raw capture proves
# all three alternate wave-4 NORMAL action decisions, not original 2022 AI.
ai=json.loads((D/'bf_m10_alternate_2014_action_evidence_v413.json').read_text('utf8'))
assert ai['schema']=='bf-global-2014-m10-alternate-normal-attack-evidence-v413'
assert ai['sourceEra']==2014 and ai['missionId']==10 and ai['wave']==4
assert ai['original2022Confirmed'] is False
assert ai['changesCanonicalBattle'] is False and ai['changesRewardsOrSave'] is False
assert ai['source']['gitBlobSha']==alt['alternate']['gitBlobSha']
assert ai['source']['sourcePath']==alt['alternate']['sourcePath']
assert ai['normalAttack']=={
 'type':'attack','parameters':'-1','percent':100,
 'targetCondition':'random','targetType':2,'conditions':0,
 'actionsPerTurn':'1~1','skills':0}
assert len(ai['enemies'])==len(alt['wave4Alternate'])==3
assert [dict((k,e[k]) for k in ('name','unitId','hp','atk','def','aiId'))
         for e in ai['enemies']]==alt['wave4Alternate']
assert [e['slot'] for e in ai['enemies']]==[0,1,2]
fixture={'schema':'bf-global-2014-historical-wave-lab-v200',
         'provenance':{
            'url':'https://github.com/cheahjs/bravefrontier_data',
            'era':'historical 2014 Global parser snapshots',
            'notice':'Not established as original 2022 enemy formations or battle mechanics. All practice gameplay is experimental, reward-free and isolated.'},
         'totals':totals,'missions':rows}
json_text=json.dumps(fixture,indent=2,ensure_ascii=True)+'\n'
generated=D/'bf_global_historical_wave_lab_v200.json'
if generated.exists():assert generated.read_text('utf8')==json_text,'Source-derived data diverged'
else:generated.write_text(json_text,'utf8')
asset=A/'bf200_historical_wave_lab.js'
s=asset.read_text('utf8')
prepared='/* BF200_DATA_READY */'+json.dumps(
    fixture,separators=(',',':'),ensure_ascii=True).replace('<',r'\u003c')
placeholder='/* BF200_DATA_PLACEHOLDER */null'
if placeholder in s:
    assert s.count(placeholder)==1
    s=s.replace(placeholder,prepared,1)
    asset.write_text(s,'utf8')
else:
    assert s.count(prepared)==1 and s.count('BF200_DATA_PLACEHOLDER')==0
# Insert separately pinned 2014 alternate data into the same bounded offline asset.
alt_prepared='/* BF200_M10_ALT_READY */'+json.dumps(
    alt,separators=(',',':'),ensure_ascii=True).replace('<',r'\\u003c')
alt_placeholder='/* BF200_M10_ALT_PLACEHOLDER */null'
if alt_placeholder in s:
    assert s.count(alt_placeholder)==1
    s=s.replace(alt_placeholder,alt_prepared,1)
    asset.write_text(s,'utf8')
else:
    assert s.count(alt_prepared)==1 and 'BF200_M10_ALT_PLACEHOLDER' not in s
# Bundle the local, original-2014-only attack evidence beside the alternate
# roster. Byte size/JS parser remain mandatory; no network or user save.
ai_prepared='/* BF200_M10_AI_READY */'+json.dumps(
    ai,separators=(',',':'),ensure_ascii=True).replace('<',r'\u003c')
ai_placeholder='/* BF200_M10_AI_PLACEHOLDER */null'
if ai_placeholder in s:
    assert s.count(ai_placeholder)==1
    s=s.replace(ai_placeholder,ai_prepared,1)
    asset.write_text(s,'utf8')
else:
    assert s.count(ai_prepared)==1 and 'BF200_M10_AI_PLACEHOLDER' not in s
assert len(s.encode('utf8'))<65536,'WebView local JS resource must be under 64KiB'
assert s.count('/* BF_GLOBAL_ARCHIVE_TRIALS_V200 */')==1
print('PASS source-attributed 2014 archive: 21 quests, 112 wave groups, 264 enemy slots, 42 unique IDs, no 2022 gameplay changes')
