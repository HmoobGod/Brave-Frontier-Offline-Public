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
assert len(s.encode('utf8'))<65536,'WebView local JS resource must be under 64KiB'
assert s.count('/* BF_GLOBAL_ARCHIVE_TRIALS_V200 */')==1
print('PASS source-attributed 2014 archive: 21 quests, 112 wave groups, 264 enemy slots, 42 unique IDs, no 2022 gameplay changes')
